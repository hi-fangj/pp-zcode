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

FUSION_SKILLS = ["pipeline", "pipeline-accept", "pipeline-execute"]
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


class TestReferences(unittest.TestCase):
    def test_referenced_playbooks_exist(self):
        execute = (SKILLS / "pipeline-execute" / "SKILL.md").read_text()
        for ref in set(re.findall(r"playbooks/([a-z-]+)\.md", execute)):
            self.assertTrue((SKILLS / "pipeline-execute" / "playbooks" / f"{ref}.md").is_file(),
                            f"pipeline-execute references missing playbook {ref}")

    def test_expected_playbooks_shipped(self):
        for pb in PLAYBOOKS:
            self.assertTrue((SKILLS / "pipeline-execute" / "playbooks" / f"{pb}.md").is_file(),
                            f"playbook {pb} went missing")

    def test_pipeline_reference_files_exist(self):
        for ref in ("handoff-brief.md", "target-agents-snippet.md"):
            self.assertTrue((SKILLS / "pipeline" / "references" / ref).is_file())

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

    def test_pipeline_gate_names_are_consistent(self):
        router = (SKILLS / "pipeline" / "SKILL.md").read_text()
        accept = (SKILLS / "pipeline-accept" / "SKILL.md").read_text()
        for stage in ("grilling", "to-spec", "to-tickets", "pipeline-execute"):
            self.assertIn(stage, router, f"pipeline router lost its {stage} stage")
        for verdict in ("pass", "fail", "unverified"):
            self.assertIn(verdict, accept, f"pipeline-accept lost its {verdict} verdict")


class TestPipelineStatus(unittest.TestCase):
    def test_mirrors_pipeline_stage_names(self):
        status = (SKILLS / "pipeline-status" / "SKILL.md").read_text()
        for stage in ("grilling", "to-spec", "to-tickets", "pipeline-execute", "pipeline-accept"):
            self.assertIn(stage, status, f"pipeline-status lost its {stage} stage")

    def test_stays_model_invocable(self):
        fm = frontmatter(SKILLS / "pipeline-status" / "SKILL.md")
        self.assertNotIn("disable-model-invocation", fm,
                         "pipeline-status must stay model-invocable")


if __name__ == "__main__":
    unittest.main(verbosity=2)
