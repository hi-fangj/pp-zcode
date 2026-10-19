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

FUSION_SKILLS = [
    "implement-spec",
    "poteto-mode",
    "pipeline-accept",
    "ask",
    "interrogate",
    "setup-models",
]
UNITY_SKILLS = ["unity-development", "unity-development-setup"]
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
UPSTREAM_SKILLS = [
    "blast-radius",
    "correct",
    "teach",
    "show-me-your-work",
    "typescript-best-practices",
    "reflect",
    "recall",
    "create-verification-skill",
    "maintain-verification-skill",
    "create-formal-verification-skill",
    "maintain-formal-verification-skill",
]
BUNDLED_AGENTS = ["comment-sicko"]
BUNDLED_SKILL_NAMES = sorted(set(FUSION_SKILLS + POCOCK_SKILLS + UNITY_SKILLS + UPSTREAM_SKILLS + [
    "pipeline-status",
    "how",
    "why",
    "architect",
    "arena",
    "swarm",
    "interrogate",
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
    "session-pickup",
    "pause-safely",
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


class TestPluginIcon(unittest.TestCase):
    """The marketplace icon is loaded by the ZCode renderer as a remote <img>,
    so the catalog must point at an https URL whose path mirrors the shipped
    asset. A private repository at that URL renders no icon."""

    def test_marketplace_icon_is_https_and_names_the_shipped_asset(self):
        entry = json.loads((REPO / "marketplace.json").read_text())["plugins"][0]
        icon = entry.get("icon", "")
        self.assertTrue(icon.startswith("https://"),
                        "plugin icon must be an https URL")
        self.assertTrue(icon.endswith("/assets/icon.png"),
                        "plugin icon URL must point at assets/icon.png")

    def test_png_ships_at_512_square(self):
        data = (REPO / "assets" / "icon.png").read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n", "icon.png is not a PNG")
        width = int.from_bytes(data[16:20], "big")
        height = int.from_bytes(data[20:24], "big")
        self.assertEqual((width, height), (512, 512),
                         "ZCode plugin icons ship at 512x512")

    def test_svg_source_ships_and_matches_the_png_canvas(self):
        svg = (REPO / "assets" / "icon.svg").read_text(encoding="utf-8")
        self.assertTrue(svg.lstrip().startswith("<svg"), "icon.svg is not SVG")
        self.assertIn('viewBox="0 0 512 512"', svg)
        self.assertNotIn("{{", svg, "icon.svg contains an unresolved placeholder")


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
                if name in BUNDLED_AGENTS:
                    continue
                self.assertTrue((SKILLS / name / "SKILL.md").is_file(),
                                f"{path.relative_to(SKILLS)} references pp-zcode:{name}, "
                                "which is not bundled")


class TestBundledAgents(unittest.TestCase):
    """no-comments spawns a reviewer subagent. The plugin registers it under
    agents/ so the spawn does not depend on a user-level install."""

    def test_every_agent_ships_with_matching_frontmatter(self):
        for name in BUNDLED_AGENTS:
            path = PLUGIN / "agents" / f"{name}.md"
            self.assertTrue(path.is_file(), f"agents/{name}.md went missing")
            self.assertEqual(frontmatter(path).get("name"), name,
                             f"agents/{name}.md frontmatter name mismatch")

    def test_manifest_declares_the_agents_directory(self):
        manifest = json.loads((PLUGIN / ".zcode-plugin" / "plugin.json").read_text())
        self.assertEqual(manifest.get("agents"), "./agents")
        self.assertTrue((PLUGIN / "agents").is_dir())


class TestHarnessResidue(unittest.TestCase):
    """Cursor mechanics have no zcode equivalent. A stale mention sends the agent
    looking for a tool or command that does not exist on this host."""

    FORBIDDEN = [
        (re.compile(r"cursor-team-kit"), "Cursor team-kit command"),
        (re.compile(r"Cursor cloud agent"), "Cursor cloud agent"),
        (re.compile(r"Cursor'?s? `?/loop`?"), "Cursor /loop"),
        (re.compile(r"`Task` (?:tool|spawn|spawns|calls|call)"), "Task tool"),
        (re.compile(r"Spawn(?:ing)? (?:a |multiple |several )?`Task`"), "Task tool spawn"),
        (re.compile(r"\bgeneralPurpose\b"), "wrong subagent type name"),
        (re.compile(r"(?<![\w:])`comment-sicko`"), "unqualified agent name"),
        (re.compile(r'"comment-sicko"'), "unqualified agent name"),
        (re.compile(r"(?:from|in) the Cursor environment"), "Cursor MCP discovery"),
        (re.compile(r"`mcps/` directory"), "Cursor MCP discovery"),
        (re.compile(r"cursor location"), "editor cursor signal"),
    ]
    # The Harness adapter and Substitutions tables name upstream mechanics on
    # purpose. Exemption is exact-line equality, so appended forbidden text
    # still fails.
    ALLOWED_ROWS = {
        "| `Task` tool | `Agent` tool |",
        "| `deslop` from cursor-team-kit | The bundled `pp-zcode:unslop` and `pp-zcode:no-comments` skills cover it. |",
        "| Cursor `/loop` | Re-invoke the step each round, or read the background task's output file; a background agent notifies on completion. |",
        "| Bugbot, Cursor cloud agents, Automations, built-in PR tool | Skip with one line `Skipped in zcode: <step>. <reason>.` and continue. Use `gh` for PR operations. |",
    }

    def _bundled_texts(self):
        return list(SKILLS.rglob("*.md")) + list((PLUGIN / "agents").rglob("*.md"))

    def test_no_cursor_mechanics_in_bundled_text(self):
        for path in sorted(self._bundled_texts()):
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if line.strip() in self.ALLOWED_ROWS:
                    continue
                for pattern, label in self.FORBIDDEN:
                    self.assertIsNone(
                        pattern.search(line),
                        f"{path.relative_to(PLUGIN)}:{lineno} still uses {label}")

    def test_skill_frontmatter_uses_only_supported_keys(self):
        """ZCode reads name, description, and disable-model-invocation. A key
        copied from another host (`paths`, `icon`, `color`) is silently ignored,
        which makes the trigger the author intended never fire."""
        allowed = {"name", "description", "disable-model-invocation"}
        for name, path in skill_dirs().items():
            keys = set(frontmatter(path))
            self.assertEqual(keys - allowed, set(),
                             f"{name}/SKILL.md carries unsupported frontmatter "
                             f"keys: {sorted(keys - allowed)}")


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
                        "no-comments needs its fallback agent brief")

    def test_comment_sicko_fallback_matches_the_agent(self):
        """README promises the fallback inlines the same brief. Drift between the
        two copies means a host without plugin agents gets different rules."""
        brief = SKILLS / "no-comments" / "references" / "comment-sicko.md"
        agent = PLUGIN / "agents" / "comment-sicko.md"
        self.assertEqual(brief.read_text(encoding="utf-8"),
                         agent.read_text(encoding="utf-8"),
                         "no-comments fallback brief drifted from the agent")

    def test_upstream_skills_ship_their_support_files(self):
        support = {
            "show-me-your-work": ["references/decision-log-template.tsv",
                                  "scripts/log.sh"],
            "typescript-best-practices": ["references/patterns.md"],
            "reflect": ["references/judgment-reviewer.md",
                        "references/tooling-reviewer.md",
                        "references/divergent-reviewer.md",
                        "references/synthesizer.md"],
            "create-verification-skill": [
                "references/feature-map-example/README.md",
                "references/feature-map-example/create-note.md",
                "references/feature-map-example/search.md",
            ],
        }
        for name, refs in support.items():
            for ref in refs:
                self.assertTrue((SKILLS / name / ref).is_file(),
                                f"{name} is missing {ref}")

    def test_session_helpers_ship(self):
        self.assertTrue(
            (SKILLS / "poteto-mode" / "scripts" / "session-store.py").is_file(),
            "recall and session-pickup need the read-only session store helper")

    def test_backticked_support_paths_resolve(self):
        """A skill that tells the agent to read `references/x.md` and ships no such
        file strands the run. Only concrete paths count; prose examples stay out."""
        pattern = re.compile(
            r"`(references/[A-Za-z0-9_./-]+\.md|scripts/[A-Za-z0-9_./-]+\.(?:py|sh))`")
        for path in sorted(SKILLS.rglob("*.md")):
            for ref in set(pattern.findall(path.read_text(encoding="utf-8"))):
                self.assertTrue((path.parent / ref).is_file(),
                                f"{path.relative_to(SKILLS)} cites missing {ref}")


class TestFusionContent(unittest.TestCase):
    """The skills authored for this plugin must not ship template leftovers."""

    def test_no_unresolved_placeholders_in_fusion_skills(self):
        for name in FUSION_SKILLS + UNITY_SKILLS:
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


class TestUnitySkills(unittest.TestCase):
    """The Unity pair mirrors the per-repository setup the local Unity repos
    already use: one execution skill and one setup skill that writes the project
    validation matrix agents read before a change."""

    def test_execution_skill_ships_its_verification_reference(self):
        self.assertTrue(
            (SKILLS / "unity-development" / "references" / "verification.md").is_file(),
            "unity-development is missing references/verification.md")

    def test_setup_ships_the_project_doc_template(self):
        self.assertTrue(
            (SKILLS / "unity-development-setup" / "references" / "unity-development-doc.md").is_file(),
            "unity-development-setup is missing its doc template")

    def test_execution_skill_is_model_invocable(self):
        fm = frontmatter(SKILLS / "unity-development" / "SKILL.md")
        self.assertNotIn("disable-model-invocation", fm,
                         "unity-development must stay model-invocable")

    def test_setup_stays_user_invoked(self):
        fm = frontmatter(SKILLS / "unity-development-setup" / "SKILL.md")
        self.assertEqual(fm.get("disable-model-invocation"), "true",
                         "unity-development-setup must stay user-invoked")

    def test_setup_writes_the_documented_contract(self):
        setup = (SKILLS / "unity-development-setup" / "SKILL.md").read_text()
        self.assertIn("docs/agents/unity-development.md", setup,
                      "setup must write the project verification matrix")
        self.assertIn("### Unity development", setup,
                      "setup must declare the Unity development agent block")

    def test_engine_routes_unity_repositories_to_the_skill(self):
        engine = (SKILLS / "poteto-mode" / "SKILL.md").read_text()
        self.assertIn("pp-zcode:unity-development", engine,
                      "poteto-mode must load the Unity skill for Unity repositories")


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
        "teach",
        "blast-radius",
        "architect",
        "arena",
        "swarm",
        "interrogate",
        "technical-writing",
        "unslop",
        "no-comments",
        "benchmark-checklist",
        "domain-modeling",
        "codebase-design",
        "setup-matt-pocock-skills",
        "setup-models",
        "unity-development",
        "unity-development-setup",
        "typescript-best-practices",
        "correct",
        "show-me-your-work",
        "recall",
        "reflect",
        "create-verification-skill",
        "maintain-verification-skill",
        "create-formal-verification-skill",
        "maintain-formal-verification-skill",
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


class TestModelRoles(unittest.TestCase):
    """Model roles live in one host data file, not in model slugs baked into skills.
    A skill that still names a Cursor rule or a hardcoded slug silently ignores the
    user's configuration."""

    MODELS_FILE = "~/.zcode/pp-zcode/models.md"

    def test_no_cursor_model_rule_survives(self):
        for path in sorted(SKILLS.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("pstack-models.mdc", text,
                             f"{path.relative_to(SKILLS)} still reads the Cursor rule")

    def test_no_hardcoded_model_slugs(self):
        slugs = re.compile(r"\b(?:claude-opus|grok|composer)-[a-z0-9.-]+")
        for path in sorted(SKILLS.rglob("*.md")):
            match = slugs.search(path.read_text(encoding="utf-8"))
            self.assertIsNone(match,
                              f"{path.relative_to(SKILLS)} hardcodes model slug "
                              f"{match.group(0) if match else ''}")

    def test_role_reading_skills_name_the_data_file(self):
        for name in ("arena", "swarm", "how", "why", "architect", "interrogate",
                     "reflect", "poteto-mode", "setup-models"):
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(self.MODELS_FILE, text,
                          f"{name} must read {self.MODELS_FILE}")

    def test_upstream_skills_ship(self):
        for name in UPSTREAM_SKILLS:
            self.assertTrue((SKILLS / name / "SKILL.md").is_file(),
                            f"upstream skill {name} went missing")

    def test_integrated_upstream_skills_are_model_invocable(self):
        """poteto-mode opens a decision trail mid-run and type-system-discipline
        points at the TS skill, so neither may be user-invoked only."""
        for name in ("show-me-your-work", "typescript-best-practices"):
            fm = frontmatter(SKILLS / name / "SKILL.md")
            self.assertNotIn("disable-model-invocation", fm,
                             f"{name} must stay model-invocable for its caller")

    def test_new_entry_skills_stay_user_invoked(self):
        for name in ("blast-radius", "correct", "teach", "reflect", "recall",
                     "create-verification-skill", "maintain-verification-skill",
                     "create-formal-verification-skill",
                     "maintain-formal-verification-skill"):
            fm = frontmatter(SKILLS / name / "SKILL.md")
            self.assertEqual(fm.get("disable-model-invocation"), "true",
                             f"{name} must stay user-invoked")

    def test_skills_that_read_role_lines_name_the_data_file(self):
        """A skill that picks a model must read the configured table, or it
        silently degrades to the session model."""
        for name in ("show-me-your-work", "recall"):
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(self.MODELS_FILE, text,
                          f"{name} must read {self.MODELS_FILE}")

    def test_every_role_line_is_written_by_setup(self):
        setup = (SKILLS / "setup-models" / "SKILL.md").read_text(encoding="utf-8")
        for role in (
            "feature, refactoring",
            "bug-fix",
            "hardest tasks",
            "judgment and prose",
            "how explorer",
            "how explainer",
            "why investigators",
            "why synthesizer",
            "arena runners",
            "arena cross-judge pool",
            "swarm workers",
            "architect runners",
            "interrogate reviewers",
            "reflect judgment, divergent, synthesizer",
            "reflect tooling",
        ):
            self.assertIn(role, setup, f"setup-models dropped the {role} role")

    def test_interrogate_ships_its_review_material(self):
        for ref in ("reviewer-prompt.md", "rubric.md", "code-quality-review.md",
                    "lead-judgment.md"):
            self.assertTrue((SKILLS / "interrogate" / "references" / ref).is_file(),
                            f"interrogate is missing references/{ref}")

    def test_interrogate_and_setup_stay_user_invoked(self):
        for name in ("interrogate", "setup-models"):
            fm = frontmatter(SKILLS / name / "SKILL.md")
            self.assertEqual(fm.get("disable-model-invocation"), "true",
                             f"{name} must stay user-invoked")


if __name__ == "__main__":
    unittest.main(verbosity=2)
