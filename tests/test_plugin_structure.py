"""Structural tests for the pp-zcode plugin.

The repo ships no runtime code; the plugin IS a set of markdown skills plus
manifests. These tests pin the invariants the zcode loader and the pipeline
depend on, so an edit that breaks naming, frontmatter, or referenced files
fails before it is pushed.

Run from anywhere:  python3 -m unittest discover -s tests -v
"""

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "plugins" / "pp-zcode"
SKILLS = PLUGIN / "skills"

FUSION_SKILLS = ["implement-spec", "poteto-mode", "pipeline-accept", "ask"]
POCOCK_SKILLS = [
    "grilling",
    "grill-me",
    "grill-with-docs",
    "domain-modeling",
    "to-spec",
    "to-tickets",
    "setup-matt-pocock-skills",
    "tdd",
    "codebase-design",
    "triage",
]
POCOCK_USER_INVOKED = [
    "grill-me",
    "grill-with-docs",
    "to-spec",
    "to-tickets",
    "setup-matt-pocock-skills",
    "triage",
]
POCOCK_MODEL_INVOCABLE = ["grilling", "domain-modeling", "tdd", "codebase-design"]
POCOCK_REFERENCE_FILES = {
    "domain-modeling": ["ADR-FORMAT.md", "GLOSSARY-FORMAT.md"],
    "setup-matt-pocock-skills": [
        "domain.md",
        "issue-tracker-github.md",
        "issue-tracker-gitlab.md",
        "issue-tracker-local.md",
        "triage-labels.md",
    ],
    "tdd": ["mocking.md", "tests.md"],
    "codebase-design": ["DEEPENING.md", "DESIGN-IT-TWICE.md"],
    "triage": ["AGENT-BRIEF.md", "OUT-OF-SCOPE.md"],
}
BUNDLED_SKILL_NAMES = sorted(set(FUSION_SKILLS + POCOCK_SKILLS + [
    "pipeline-status",
    "how",
    "why",
    "architect",
    "arena",
    "swarm",
    "unslop",
    "no-comments",
    "technical-writing",
    "benchmark-checklist",
]))
PLAYBOOKS = [
    "investigation",
    "bug-fix",
    "feature",
    "refactoring",
    "prototype",
    "shipping",
    "opening-a-pr",
]


def frontmatter(path: Path) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).splitlines():
        m = re.match(r"^([A-Za-z-]+):\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip('"')
    return fields


def skill_dirs() -> dict:
    return {
        d.name: d / "SKILL.md"
        for d in sorted(SKILLS.iterdir())
        if d.is_dir()
    }


class TestManifest(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((PLUGIN / ".zcode-plugin" / "plugin.json").read_text())

    def test_name_matches_directory(self):
        self.assertEqual(self.manifest["name"], PLUGIN.name)

    def test_version_is_semver(self):
        self.assertRegex(self.manifest["version"], r"^\d+\.\d+\.\d+$")

    def test_declared_components_exist(self):
        for key in ("skills",):
            self.assertIn(key, self.manifest)
            self.assertTrue((PLUGIN / self.manifest[key]).is_dir(),
                            f"{key} path does not resolve")


class TestMarketplace(unittest.TestCase):
    def setUp(self):
        self.market = json.loads((REPO / "marketplace.json").read_text())
        self.plugin = json.loads((PLUGIN / ".zcode-plugin" / "plugin.json").read_text())

    def test_entry_matches_plugin_manifest(self):
        entry = self.market["plugins"][0]
        self.assertEqual(entry["name"], self.plugin["name"])
        self.assertEqual(entry["version"], self.plugin["version"])

    def test_source_path_resolves_to_plugin(self):
        entry = self.market["plugins"][0]
        source = REPO / entry["source"]
        self.assertTrue((source / ".zcode-plugin" / "plugin.json").is_file())

    def test_single_catalog_at_repo_root(self):
        """The GitHub repo itself is the marketplace source; a second catalog
        elsewhere would shadow or diverge from the root one."""
        found = [p for p in REPO.rglob("marketplace.json")
                 if ".git" not in p.parts]
        self.assertEqual(found, [REPO / "marketplace.json"])


class TestSkills(unittest.TestCase):
    def test_every_skill_dir_has_skill_md(self):
        for name, path in skill_dirs().items():
            self.assertTrue(path.is_file(), f"{name}/ is missing SKILL.md")

    def test_frontmatter_name_matches_directory(self):
        for name, path in skill_dirs().items():
            fm = frontmatter(path)
            self.assertTrue(fm, f"{name}/SKILL.md has no frontmatter block")
            self.assertEqual(fm.get("name"), name,
                             f"{name}/SKILL.md frontmatter name mismatch")

    def test_every_skill_has_description(self):
        for name, path in skill_dirs().items():
            desc = frontmatter(path).get("description", "")
            self.assertTrue(desc, f"{name}/SKILL.md has an empty description")

    def test_no_duplicate_skill_names(self):
        names = [frontmatter(p).get("name") for p in skill_dirs().values()]
        self.assertEqual(len(names), len(set(names)))

    def test_user_invoked_skills_opt_out_of_model_invocation(self):
        for name in FUSION_SKILLS:
            fm = frontmatter(SKILLS / name / "SKILL.md")
            self.assertEqual(fm.get("disable-model-invocation"), "true",
                             f"{name} must stay user-invoked")


class TestBundledPocockSkills(unittest.TestCase):
    """Matt Pocock's requirements skills ship inside the plugin, so a user-level
    install of the same name is not required and cannot shadow the qualified name."""

    def test_every_bundled_skill_ships(self):
        for name in POCOCK_SKILLS:
            self.assertTrue((SKILLS / name / "SKILL.md").is_file(),
                            f"bundled Pocock skill {name} went missing")

    def test_reference_files_ship_with_their_skill(self):
        for name, refs in POCOCK_REFERENCE_FILES.items():
            for ref in refs:
                self.assertTrue((SKILLS / name / ref).is_file(),
                                f"{name} is missing reference file {ref}")

    def test_invocation_policy_matches_upstream(self):
        for name in POCOCK_USER_INVOKED:
            fm = frontmatter(SKILLS / name / "SKILL.md")
            self.assertEqual(fm.get("disable-model-invocation"), "true",
                             f"{name} must stay user-invoked")
        for name in POCOCK_MODEL_INVOCABLE:
            fm = frontmatter(SKILLS / name / "SKILL.md")
            self.assertNotIn("disable-model-invocation", fm,
                             f"{name} must stay model-invocable")

    def test_cross_references_use_qualified_names(self):
        """A bare skill name resolves through an alias that a user-level skill of
        the same name shadows, so every invocation and routing line must carry the
        plugin prefix."""
        bare_slash = re.compile(
            r"(?<![\w:./-])/(?:" + "|".join(re.escape(n) for n in BUNDLED_SKILL_NAMES) + r")\b")
        bare_call = re.compile(
            r'Skill tool (?:with|twice, for) "(?:'
            + "|".join(re.escape(n) for n in BUNDLED_SKILL_NAMES) + r')"')
        for path in sorted(SKILLS.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(bare_slash.search(text),
                              f"{path.relative_to(SKILLS)} invokes a bundled skill by bare name")
            self.assertIsNone(bare_call.search(text),
                              f"{path.relative_to(SKILLS)} calls a bundled skill by bare name")

    def test_bundled_skills_have_no_unresolved_placeholders(self):
        for name in POCOCK_SKILLS:
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("{{", text, f"{name} contains an unresolved placeholder")

    def test_qualified_references_resolve(self):
        """A typo in a pp-zcode:<name> reference silently breaks routing at run time."""
        pattern = re.compile(r"pp-zcode:([a-z0-9][a-z0-9-]*[a-z0-9])(?![a-z0-9<-])")
        for path in sorted(SKILLS.rglob("*.md")):
            for name in sorted(set(pattern.findall(path.read_text(encoding="utf-8")))):
                self.assertTrue((SKILLS / name / "SKILL.md").is_file(),
                                f"{path.relative_to(SKILLS)} references pp-zcode:{name}, "
                                "which is not bundled")


class TestReferences(unittest.TestCase):
    def test_referenced_playbooks_exist(self):
        engine = (SKILLS / "poteto-mode" / "SKILL.md").read_text()
        for ref in set(re.findall(r"playbooks/([a-z-]+)\.md", engine)):
            self.assertTrue((SKILLS / "poteto-mode" / "playbooks" / f"{ref}.md").is_file(),
                            f"poteto-mode references missing playbook {ref}")

    def test_expected_playbooks_shipped(self):
        for pb in PLAYBOOKS:
            self.assertTrue((SKILLS / "poteto-mode" / "playbooks" / f"{pb}.md").is_file(),
                            f"playbook {pb} went missing")

    def test_implement_spec_reference_files_exist(self):
        for ref in ("handoff-brief.md", "target-agents-snippet.md"):
            self.assertTrue((SKILLS / "implement-spec" / "references" / ref).is_file())

    def test_comment_sicko_brief_vendored(self):
        brief = SKILLS / "no-comments" / "references" / "comment-sicko.md"
        self.assertTrue(brief.is_file(),
                        "no-comments needs its relocated agent brief")


class TestFusionContent(unittest.TestCase):
    """The skills authored for this plugin must not ship template leftovers."""

    def test_no_unresolved_placeholders_in_fusion_skills(self):
        for name in FUSION_SKILLS:
            text = (SKILLS / name / "SKILL.md").read_text()
            self.assertNotIn("{{", text, f"{name} contains an unresolved placeholder")

    def test_bridge_and_engine_wiring_is_consistent(self):
        bridge = (SKILLS / "implement-spec" / "SKILL.md").read_text()
        engine = (SKILLS / "poteto-mode" / "SKILL.md").read_text()
        accept = (SKILLS / "pipeline-accept" / "SKILL.md").read_text()
        self.assertIn("poteto-mode", bridge, "implement-spec must name its engine")
        self.assertIn("pipeline-accept", bridge, "implement-spec must route spec-backed runs to acceptance")
        self.assertIn("implement-spec", engine, "poteto-mode must name its front-door bridge")
        self.assertIn("Ticketless", engine, "poteto-mode lost its ticketless brief branch")
        for verdict in ("pass", "fail", "unverified"):
            self.assertIn(verdict, accept, f"pipeline-accept lost its {verdict} verdict")


class TestRouter(unittest.TestCase):
    """pp-zcode:ask is the discovery surface. A routable skill that it fails to
    name is a skill the user has to remember, which is the problem it exists to
    solve."""

    ROUTED_SKILLS = [
        "grilling",
        "grill-me",
        "grill-with-docs",
        "to-spec",
        "to-tickets",
        "implement-spec",
        "poteto-mode",
        "pipeline-accept",
        "pipeline-status",
        "triage",
        "tdd",
        "how",
        "why",
        "architect",
        "arena",
        "swarm",
        "technical-writing",
        "unslop",
        "no-comments",
        "benchmark-checklist",
        "domain-modeling",
        "codebase-design",
        "setup-matt-pocock-skills",
    ]

    def test_names_every_routable_skill(self):
        text = (SKILLS / "ask" / "SKILL.md").read_text(encoding="utf-8")
        for name in self.ROUTED_SKILLS:
            self.assertIn(f"pp-zcode:{name}", text,
                          f"the router lost its route to {name}")

    def test_stays_user_invoked(self):
        fm = frontmatter(SKILLS / "ask" / "SKILL.md")
        self.assertEqual(fm.get("disable-model-invocation"), "true",
                         "the router must not be invoked by the model on its own")


class TestPipelineStatus(unittest.TestCase):
    def test_mirrors_pipeline_stage_names(self):
        status = (SKILLS / "pipeline-status" / "SKILL.md").read_text()
        for stage in ("grilling", "to-spec", "to-tickets", "implement-spec",
                      "poteto-mode", "pipeline-accept"):
            self.assertIn(stage, status, f"pipeline-status lost its {stage} stage")

    def test_stays_model_invocable(self):
        fm = frontmatter(SKILLS / "pipeline-status" / "SKILL.md")
        self.assertNotIn("disable-model-invocation", fm,
                         "pipeline-status must stay model-invocable")


if __name__ == "__main__":
    unittest.main(verbosity=2)
