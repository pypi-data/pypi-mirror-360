import ipaddress
import gzip
import tempfile
import weakref
import shutil
import re

from io import BytesIO
from pymisp import PyMISP, MISPEvent, MISPObject
from pymisp.tools import FileObject
from pykunai.event import Event
from pykunai.graph import KunaiGraph
from typing import List
from urllib.parse import urlparse

URL_RE = re.compile(r"\b[^\s]+://[^\s]+")


def is_valid_ip_address(ip_str: str) -> bool:
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def misp_object_to_tuple(mo: MISPObject):
    out = []
    for a in mo.attributes:
        out.append((a.object_relation, a.value))
    return tuple(out)


def compress_file(input_file):
    with open(input_file, "rb") as f_in:
        with tempfile.NamedTemporaryFile() as tmp:
            with gzip.open(tmp.name, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            return tmp.read()


def find_object_by_uuid(misp: MISPEvent, uuid: str):
    for o in misp.objects:
        if o.uuid == uuid:
            return o


class KunaiMispEvent:
    def __init__(self, trace: List[Event], misp: PyMISP = None) -> None:
        self._sample_path = None
        self._sample_object = None
        self._events = trace
        self._caches = {}
        self._mitre_attack = set()
        self._misp = misp
        self._entrypoint = None
        self._dropped = set()
        # hashmap mapping kunai task guuid to misp uuid
        self._kunai_to_misp_mapping = {}
        # list((src, dst, type))
        self._relations = set()
        self._log_file = tempfile.NamedTemporaryFile(mode="w+", prefix="kunai-to-misp-")
        weakref.finalize(self, self.cleanup)

    def cleanup(self):
        self._log_file.close()

    def _cache(self, key: str, o: object) -> bool:
        """
        return true if value was already in cache
        """
        ret = False
        if key not in self._caches:
            self._caches[key] = set()
        # should be true if value is already there
        ret = o in self._caches[key]
        self._caches[key].add(o)
        return ret

    def _cache_misp_object(self, key: str, o: MISPObject) -> bool:
        """
        return true if value was already in cache
        """
        ret = False
        if key not in self._caches:
            self._caches[key] = set()
        t = misp_object_to_tuple(o)
        # should be true if value is already there
        ret = t in self._caches[key]
        self._caches[key].add(t)
        return ret

    def with_sample(self, sample_path: str) -> None:
        self._sample_path = sample_path
        self._sample_object = FileObject(filepath=self._sample_path)
        self._sample_object.comment = "Malware Sample Analyzed"

    def _finalize(self, misp_event: MISPEvent, graph: None) -> None:
        if self._sample_path is None:
            return None

        if self._entrypoint is not None:
            self._sample_object.first_seen = self._entrypoint.utc_time_str

        # we add the activity graph if necessary
        if graph is not None:
            self._sample_object.add_attribute(
                "attachment",
                value="activity-graph.svg",
                data=BytesIO(graph.to_svg_bytes()),
                disable_correlation=True,
                comment="sample activity graph",
            )

        self._log_file.flush()

        self._sample_object.add_attribute(
            "attachment",
            value="kunai.json.gz",
            data=BytesIO(compress_file(self._log_file.name)),
            disable_correlation=True,
            comment="kunai logs for sample",
        )

        misp_event.add_object(self._sample_object)

    def _update_with_event(self, misp_event: MISPEvent, kunai_event: Event) -> None:
        ty = kunai_event.type_str

        # we update the time of the first event
        if self._entrypoint is None:
            self._entrypoint = kunai_event

        # we update the list of mitre attack ids
        self._mitre_attack.update(kunai_event.attack)

        if ty in ["execve", "execve_script"]:
            self._handle_execve(misp_event, kunai_event)
        if ty == "clone":
            self._handle_clone(misp_event, kunai_event)
        if ty in ["mmap_exec"]:
            self._handle_mmap_exec(misp_event, kunai_event)
        elif ty in ["connect", "send_data"]:
            self._handle_network(misp_event, kunai_event)
        elif ty == "dns_query":
            self._handle_dns_query(misp_event, kunai_event)
        elif ty in [
            "file_create",
            "write_config",
            "write",
            "write_close",
        ]:
            self._handle_file_event(misp_event, kunai_event)

        self._log_file.write(kunai_event.json())
        self._log_file.write("\n")
        self._log_file.flush()

    def _add_relation(self, src: str, dst: str, ty: str) -> None:
        self._relations.add((src, dst, ty))

    def _add_relation_with_kunai_guuid(
        self, kunai_guuid: str, dst: str, ty: str
    ) -> None:
        if kunai_guuid in self._kunai_to_misp_mapping:
            self._add_relation(self._kunai_to_misp_mapping[kunai_guuid], dst, ty)

    def _create_relations(self, misp: MISPEvent) -> None:
        for src, dst, ty in self._relations:
            o = find_object_by_uuid(misp, src)
            if o is not None:
                print(f"add reference src={src} dst={dst} ty={ty}")
                o.add_reference(dst, ty)

    def _handle_execve(self, misp_event: MISPEvent, kunai_event: Event) -> None:
        exes = [kunai_event[".data.exe"]]

        # we add interpreter if we are an execve_script
        if kunai_event.type_str == "execve_script":
            exes.append(kunai_event[".data.interpreter"])

        if kunai_event == self._entrypoint:
            # we create the mapping between kunai guuid and misp event
            if self._sample_object is not None:
                self._kunai_to_misp_mapping[kunai_event.task_guuid] = (
                    self._sample_object.uuid
                )
            # we don't need to process the entrypoint event as we
            # already have information in the sample file object
            # and we don't want to duplicate it
            if self._sample_object is not None:
                return

        for exe in exes:
            # if exe has been dropped
            if exe["path"] in self._dropped or kunai_event == self._entrypoint:
                fo = MISPObject("file")
                fo.comment = kunai_event.type_str
                fo.first_seen = kunai_event.utc_time_str
                # we add attributes
                fo.add_attribute("path", exe["path"])
                if exe["md5"] != "":
                    fo.add_attribute("md5", exe["md5"])
                    fo.add_attribute("sha1", exe["sha1"])
                    fo.add_attribute("sha256", exe["sha256"])
                    fo.add_attribute("sha512", exe["sha512"])
                if exe["size"] > 0:
                    fo.add_attribute("size-in-bytes", exe["size"])

                # if object hasn't aleady been added we add it
                if not self._cache_misp_object("execve", fo):
                    misp_event.add_object(fo)

                # we create the mapping between kunai guuid and misp event
                self._kunai_to_misp_mapping[kunai_event.task_guuid] = fo.uuid

                self._add_relation_with_kunai_guuid(
                    kunai_event.parent_task_guuid, fo.uuid, "execute"
                )

        # try to find URLs in command line
        command_line = kunai_event[".data.command_line"]
        for url in URL_RE.findall(command_line):
            purl = urlparse(url)
            # minimal condition to create url object
            if purl.netloc == "":
                continue

            uo = MISPObject("url")
            uo.first_seen = kunai_event.utc_time_str
            # add scheme
            if purl.scheme != "":
                uo.add_attribute("scheme", purl.scheme)

            dest = purl.netloc.split(":")[0]
            if is_valid_ip_address(dest):
                # add ip
                uo.add_attribute("ip", purl.netloc.split(":")[0])
            else:
                # add domain
                uo.add_attribute("domain", purl.netloc.split(":")[0])
            # add port if any
            if ":" in purl.netloc:
                uo.add_attribute("port", purl.netloc.split(":")[1])
            # add path if any
            if purl.path != "":
                uo.add_attribute("resource_path", purl.path)
            # add query string
            if purl.query != "":
                uo.add_attribute("query", purl.query)

            # add full url
            uo.add_attribute("url", url)

            # add a description
            uo.add_attribute("text", "URL seen in a command line")

            self._add_relation_with_kunai_guuid(
                kunai_event.task_guuid, uo.uuid, "use_in_cli"
            )

            misp_event.add_object(uo)

    def _handle_clone(self, misp_event: MISPEvent, kunai_event: Event) -> None:
        ptg = kunai_event.parent_task_guuid
        if ptg in self._kunai_to_misp_mapping:
            # we create an alias to the misp uuid of the task exe
            # as there is no way to materialize a clone process in
            # a MISP object
            self._kunai_to_misp_mapping[kunai_event.task_guuid] = (
                self._kunai_to_misp_mapping[ptg]
            )

    def _handle_mmap_exec(self, misp_event: MISPEvent, kunai_event: Event) -> None:
        exe = kunai_event[".data.mapped"]

        # if exe has been dropped
        if exe["path"] in self._dropped:
            fo = MISPObject("file")
            fo.comment = kunai_event.type_str
            fo.first_seen = kunai_event.utc_time_str
            # we add attributes
            fo.add_attribute("path", exe["path"])
            if exe["md5"] != "":
                fo.add_attribute("md5", exe["md5"])
                fo.add_attribute("sha1", exe["sha1"])
                fo.add_attribute("sha256", exe["sha256"])
                fo.add_attribute("sha512", exe["sha512"])
            if exe["size"] > 0:
                fo.add_attribute("size-in-bytes", exe["size"])

            # if object was cached we return
            if self._cache_misp_object("mmap_exec", fo):
                return

            self._add_relation_with_kunai_guuid(kunai_event.task_guuid, fo.uuid, "load")

            misp_event.add_object(fo)

    def _handle_network(self, misp_event: MISPEvent, kunai_event: Event) -> None:
        # we take only connection to public ips
        if not kunai_event[".data.dst.public"]:
            return None

        so = MISPObject("network-socket")
        so.first_seen = kunai_event.utc_time_str

        so.comment = kunai_event.type_str
        so.add_attribute("address-family", kunai_event[".data.socket.domain"])
        so.add_attribute("protocol", kunai_event[".data.socket.proto"])

        # we add only hostname we could resolve
        hostname = kunai_event[".data.dst.hostname"]
        if hostname != "?":
            so.add_attribute("hostname-dst", hostname)

        dst = kunai_event[".data.dst.ip"]
        # we don't process non globally reachable IP address
        if not ipaddress.ip_address(dst).is_global:
            return

        so.add_attribute("ip-dst", kunai_event[".data.dst.ip"])
        so.add_attribute("dst-port", kunai_event[".data.dst.port"])

        if self._cache_misp_object("connect", so):
            return

        # we create relation between misp objects
        self._add_relation_with_kunai_guuid(
            kunai_event.task_guuid, so.uuid, kunai_event.type_str
        )

        misp_event.add_object(so)

    def _handle_dns_query(self, misp_event: MISPEvent, kunai_event: Event) -> None:
        for ip in kunai_event[".data.response"].split(";"):
            o = MISPObject("domain-ip")
            o.first_seen = kunai_event.utc_time_str

            o.comment = kunai_event.type_str

            o.add_attribute("domain", kunai_event[".data.query"])
            o.add_attribute("ip", ip)
            o.add_attribute("last-seen", kunai_event[".info.utc_time"])
            if self._cache_misp_object("dns_query", o):
                continue
            misp_event.add_object(o)

            # create misp object relationship
            self._add_relation_with_kunai_guuid(kunai_event.task_guuid, o.uuid, "query")

    # this function can be used to handle several file events
    def _handle_file_event(self, misp_event: MISPEvent, kunai_event: Event) -> None:
        fo = MISPObject("file")

        # we process a bit type info not to create confusion in the MISP event
        ty = kunai_event.type_str
        ty.replace("write_close", "write")
        ty.replace("write_config", "write")

        fo.first_seen = kunai_event.utc_time_str

        fo.comment = ty
        path = kunai_event[".data.path"]
        fo.add_attribute("path", kunai_event[".data.path"])

        # we flag the file as being dropped
        if ty == "write":
            self._dropped.add(path)

        if self._cache_misp_object("file_create", fo):
            return

        # create misp object relationship
        self._add_relation_with_kunai_guuid(kunai_event.task_guuid, fo.uuid, ty)

        misp_event.add_object(fo)

    def _search_mitre_tags(self) -> set:
        tags = set()
        if self._misp is None:
            return tags

        for a in self._mitre_attack:
            for gc in self._misp.search_galaxy_clusters(
                # mitre attack galaxy
                "c4e851fa-775f-11e7-8163-b774922098cd",
                context="default",
                searchall=a,
            ):
                # we found the attack id
                if gc["GalaxyCluster"]["value"].endswith(a):
                    tags.add(gc["GalaxyCluster"]["tag_name"])
                    break
        return tags

    def into_misp_event(self) -> MISPEvent:
        misp_event = MISPEvent()
        misp_event.info = "Kunai Analysis Report"

        graph = KunaiGraph()

        for e in self._events:
            self._update_with_event(misp_event, e)
            graph.update(e.jq_dict())

        self._finalize(misp_event, graph)

        # we add mitre attack tags
        for tag in self._search_mitre_tags():
            misp_event.add_tag(tag)

        self._create_relations(misp_event)

        return misp_event
