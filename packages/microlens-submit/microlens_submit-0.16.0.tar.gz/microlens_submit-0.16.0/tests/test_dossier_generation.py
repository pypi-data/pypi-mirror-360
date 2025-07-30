#!/usr/bin/env python3
"""
Test script for microlens-submit dossier generation.

This script demonstrates the complete workflow:
1. Initialize a submission project
2. Add sample solutions with various model types
3. Generate a dossier
4. Open the generated HTML file in a browser

Usage:
    python tests/test_dossier_generation.py
    # or from the project root:
    python -m tests.test_dossier_generation
"""

import json
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

from microlens_submit.utils import load


def run_command(cmd, check=True, capture_output=True):
    """Run a shell command and return the result."""
    print("Running: " + cmd)
    result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
    if check and result.returncode != 0:
        print("Error running command: " + cmd)
        print("stdout: " + result.stdout)
        print("stderr: " + result.stderr)
        sys.exit(1)
    return result


def main():
    print("🚀 Testing microlens-submit dossier generation...")

    # Get the project root directory (parent of tests/)
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)  # Change to project root for consistent paths

    # Create test directories in project root
    project_dir = project_root / "test_submission_project"
    dossier_dir = project_root / "test_dossier_output"

    # Clean up any existing test directories
    if project_dir.exists():
        print("Removing existing project directory: " + str(project_dir))
        subprocess.run("rm -rf " + str(project_dir), shell=True)

    if dossier_dir.exists():
        print("Removing existing dossier directory: " + str(dossier_dir))
        subprocess.run("rm -rf " + str(dossier_dir), shell=True)

    print("\n📁 Creating test submission project...")

    # Initialize the project
    run_command("microlens-submit init --team-name 'Test Team Alpha' --tier 'advanced' " + str(project_dir))

    print("\n🔗 Setting GitHub repository URL...")

    # Set the GitHub repository URL
    run_command(
        "microlens-submit set-repo-url https://github.com/AmberLee2427/microlens-submit.git " + str(project_dir)
    )

    print("\n📊 Adding sample solutions...")

    # Add a simple 1S1L solution with alias
    run_command(
        "microlens-submit add-solution EVENT001 1S1L "
        + str(project_dir)
        + ' \
        --param t0=2459123.5 \
        --param u0=0.15 \
        --param tE=20.5 \
        --log-likelihood -1234.56 \
        --n-data-points 1250 \
        --cpu-hours 2.5 \
        --wall-time-hours 0.5 \
        --relative-probability 0.6 \
        --alias "simple_point_lens" \
        --notes "# Single Lens Solution\n\nThis is a simple point source, point lens fit for EVENT001."'
    )

    # Add a solution with elaborate markdown notes for testing
    elaborate_md = "../tests/example_note.md"
    escaped_md = elaborate_md.replace('"', '\\"').replace("\n", "\\n")
    run_command(
        "microlens-submit add-solution EVENT001 1S1L " + str(project_dir) + " "
        "--param t0=2459123.6 "
        "--param u0=0.16 "
        "--param tE=21.0 "
        "--log-likelihood -1200.00 "
        "--n-data-points 1300 "
        "--cpu-hours 3.0 "
        "--wall-time-hours 0.7 "
        "--relative-probability 0.5 "
        '--alias "detailed_analysis" '
        '--notes-file "' + escaped_md + '"'
    )

    # Add a binary lens solution with higher-order effects
    run_command(
        "microlens-submit add-solution EVENT001 1S2L "
        + str(project_dir)
        + ' \
        --param t0=2459123.5 \
        --param u0=0.12 \
        --param tE=22.1 \
        --param q=0.001 \
        --param s=1.15 \
        --param alpha=45.2 \
        --log-likelihood -1189.34 \
        --n-data-points 1250 \
        --cpu-hours 15.2 \
        --wall-time-hours 3.8 \
        --relative-probability 0.4 \
        --higher-order-effect parallax \
        --higher-order-effect finite-source \
        --t-ref 2459123.0 \
        --alias "binary_with_parallax" \
        --notes "# Binary Lens Solution\n\nThis solution includes parallax and finite source effects."'
    )

    # Add a second event with different characteristics
    run_command(
        "microlens-submit add-solution EVENT002 1S2L "
        + str(project_dir)
        + ' \
        --param t0=2459156.2 \
        --param u0=0.08 \
        --param tE=35.7 \
        --param q=0.0005 \
        --param s=0.95 \
        --param alpha=78.3 \
        --log-likelihood -2156.78 \
        --n-data-points 2100 \
        --cpu-hours 28.5 \
        --wall-time-hours 7.2 \
        --relative-probability 1.0 \
        --higher-order-effect parallax \
        --t-ref 2459156.0 \
        --alias "caustic_crossing_binary" \
        --notes "# Complex Binary Event\n\nThis event shows clear caustic crossing features."'
    )

    # Add a third event with different model type
    run_command(
        "microlens-submit add-solution EVENT003 2S1L "
        + str(project_dir)
        + ' \
        --param t0=2459180.0 \
        --param u0=0.25 \
        --param tE=18.3 \
        --log-likelihood -987.65 \
        --n-data-points 800 \
        --cpu-hours 8.1 \
        --wall-time-hours 1.5 \
        --relative-probability 1.0 \
        --alias "binary_source_model" \
        --notes "# Binary Source Event\n\nThis event shows evidence of a binary source."'
    )

    print("\n📊 Importing solutions from CSV...")

    # Import solutions from the test CSV file
    csv_file = project_root / "tests" / "data" / "test_import.csv"
    if csv_file.exists():
        print("📁 Importing from: " + str(csv_file))

        # First, do a dry run to see what would be imported
        result = run_command(
            "microlens-submit import-solutions " + str(csv_file) + " --project-path " + str(project_dir) + " --dry-run",
            check=False,
        )
        if result.returncode == 0:
            print("✅ CSV dry run successful")
            print(result.stdout)
        else:
            print("⚠️  CSV dry run had issues:")
            print(result.stdout)
            print(result.stderr)

        # Now do the actual import
        result = run_command(
            "microlens-submit import-solutions " + str(csv_file) + " --project-path " + str(project_dir),
            check=False,
        )
        if result.returncode == 0:
            print("✅ CSV import successful")
            print(result.stdout)
        else:
            print("⚠️  CSV import had issues:")
            print(result.stdout)
            print(result.stderr)
    else:
        print("⚠️  CSV file not found: " + str(csv_file))

    print("\n🔍 Validating submission...")

    # Validate the submission
    result = run_command("microlens-submit validate-submission " + str(project_dir), check=False)
    if result.returncode == 0:
        print("✅ Submission validation passed!")
    else:
        print("⚠️  Submission validation warnings (this is normal for test data):")
        print(result.stdout)

    print("\n📋 Listing solutions...")

    # List solutions for each event
    for event_id in [
        "EVENT001",
        "EVENT002",
        "EVENT003",
        "OGLE-2023-BLG-0001",
        "OGLE-2023-BLG-0002",
        "OGLE-2023-BLG-0003",
        "OGLE-2023-BLG-0004",
    ]:
        print("\n--- Solutions for " + event_id + " ---")
        result = run_command("microlens-submit list-solutions " + event_id + " " + str(project_dir))
        print(result.stdout)

    print("\n🎨 Generating dossier...")

    # Generate the dossier
    try:
        run_command("microlens-submit generate-dossier " + str(project_dir))
    except:
        print("Dossier generation failed")
        pass
    else:
        print("\n✅ Dossier generated successfully!")

    # Check what was created
    print("\n📁 Dossier files created:")
    dossier_path = project_dir / "dossier"
    for file_path in dossier_path.rglob("*"):
        if file_path.is_file():
            print("  " + str(file_path.relative_to(dossier_path)))

    # Verify the main HTML file exists
    index_html = dossier_path / "index.html"
    if not index_html.exists():
        print("❌ Error: index.html was not created!")
        sys.exit(1)

    print("📄 Main dashboard: " + str(index_html.absolute()))
    print("📁 Assets directory: " + str((dossier_path / "assets").absolute()))
    print("📁 Events directory: " + str((dossier_path / "events").absolute()))

    # Try to open the HTML file in the default browser
    print("\n🌐 Opening dashboard in browser...")
    try:
        webbrowser.open("file://" + str(index_html.absolute()))
        print("✅ Browser should have opened with the dashboard!")
    except Exception as e:
        print("⚠️  Could not automatically open browser: " + str(e))
        print("   Please manually open: " + str(index_html.absolute()))

    print("\n🎉 Test completed successfully!")
    print("\n📝 Next steps:")
    print("   1. View the dashboard in your browser")
    print("   2. Check the responsive design on different screen sizes")
    print("   3. Verify all the statistics and information are correct")
    print("   4. Test the event links (they'll be placeholders for now)")
    print("\n🧹 To clean up test files:")
    print("   rm -rf " + str(project_dir) + " " + str(dossier_dir))

    # Test that aliases are properly displayed in the dossier
    print("\n🔍 Testing alias display in dossier...")

    # Check that aliases appear in the event pages
    for event_id in [
        "EVENT001",
        "EVENT002",
        "EVENT003",
        "OGLE-2023-BLG-0001",
        "OGLE-2023-BLG-0002",
        "OGLE-2023-BLG-0003",
        "OGLE-2023-BLG-0004",
    ]:
        event_page = dossier_path / (event_id + ".html")
        if event_page.exists():
            with event_page.open("r", encoding="utf-8") as f:
                content = f.read()
                if event_id == "EVENT001":
                    # Should contain all three aliases for EVENT001
                    assert "simple_point_lens" in content, (
                        "Alias 'simple_point_lens' not found in " + event_id + ".html"
                    )
                    assert "detailed_analysis" in content, (
                        "Alias 'detailed_analysis' not found in " + event_id + ".html"
                    )
                    assert "binary_with_parallax" in content, (
                        "Alias 'binary_with_parallax' not found in " + event_id + ".html"
                    )
                elif event_id == "EVENT002":
                    assert "caustic_crossing_binary" in content, (
                        "Alias 'caustic_crossing_binary' not found in " + event_id + ".html"
                    )
                elif event_id == "EVENT003":
                    assert "binary_source_model" in content, (
                        "Alias 'binary_source_model' not found in " + event_id + ".html"
                    )
                elif event_id == "OGLE-2023-BLG-0001":
                    # Check for CSV imported aliases
                    assert "simple_1S1L" in content, "Alias 'simple_1S1L' not found in " + event_id + ".html"
                    assert "binary_parallax" in content, "Alias 'binary_parallax' not found in " + event_id + ".html"
                elif event_id == "OGLE-2023-BLG-0002":
                    assert "finite_source" in content, "Alias 'finite_source' not found in " + event_id + ".html"
                    assert "duplicate_test" in content, "Alias 'duplicate_test' not found in " + event_id + ".html"
                elif event_id == "OGLE-2023-BLG-0003":
                    assert "missing_params" in content, "Alias 'missing_params' not found in " + event_id + ".html"
                elif event_id == "OGLE-2023-BLG-0004":
                    assert "invalid_json" in content, "Alias 'invalid_json' not found in " + event_id + ".html"
            print("✅ Aliases properly displayed in " + event_id + ".html")
        else:
            print("⚠️  Event page " + event_id + ".html not found")

    # Check that aliases appear in the main dashboard
    with index_html.open("r", encoding="utf-8") as f:
        dashboard_content = f.read()
        # Should contain at least some of the aliases in the dashboard
        alias_count = sum(
            1
            for alias in [
                "simple_point_lens",
                "detailed_analysis",
                "binary_with_parallax",
                "caustic_crossing_binary",
                "binary_source_model",
                "simple_1S1L",
                "binary_parallax",
                "finite_source",
                "duplicate_test",
                "missing_params",
                "invalid_json",
            ]
            if alias in dashboard_content
        )
        if alias_count > 0:
            print("✅ Found " + str(alias_count) + " aliases in main dashboard")
        else:
            print("⚠️  No aliases found in main dashboard (this might be expected)")

    print("✅ Alias display testing completed!")

    # Test that the alias lookup table is properly created
    print("\n🔍 Testing alias lookup table...")
    alias_file = project_dir / "aliases.json"
    if alias_file.exists():
        with alias_file.open("r", encoding="utf-8") as f:
            alias_lookup = json.load(f)

        # Check that all expected aliases are in the lookup table
        expected_aliases = [
            "EVENT001 simple_point_lens",
            "EVENT001 detailed_analysis",
            "EVENT001 binary_with_parallax",
            "EVENT002 caustic_crossing_binary",
            "EVENT003 binary_source_model",
            "OGLE-2023-BLG-0001 simple_1S1L",
            "OGLE-2023-BLG-0001 binary_parallax",
            "OGLE-2023-BLG-0002 finite_source",
            "OGLE-2023-BLG-0002 duplicate_test",
            "OGLE-2023-BLG-0003 missing_params",
            "OGLE-2023-BLG-0004 invalid_json",
        ]

        for expected_alias in expected_aliases:
            assert expected_alias in alias_lookup, "Expected alias '" + expected_alias + "' not found in aliases.json"

        print("✅ Alias lookup table contains " + str(len(alias_lookup)) + " entries")
        print("✅ All expected aliases found in aliases.json")
    else:
        print("❌ Error: aliases.json was not created!")
        sys.exit(1)

    # Test editing aliases via CLI
    print("\n🔧 Testing alias editing via CLI...")

    # Get the solution ID for the first solution to edit its alias
    sub = load(str(project_dir))
    first_solution_id = next(iter(sub.get_event("EVENT001").solutions.keys()))

    # Get the original alias of the first solution
    original_alias = sub.get_event("EVENT001").solutions[first_solution_id].alias
    print("🔍 Original alias for solution " + first_solution_id[:8] + "...: '" + original_alias + "'")

    # Edit the alias of the first solution
    run_command(
        "microlens-submit edit-solution "
        + first_solution_id
        + " "
        + str(project_dir)
        + ' \
        --alias "updated_simple_lens"'
    )

    # Verify the alias was updated
    sub_updated = load(str(project_dir))
    updated_solution = sub_updated.get_event("EVENT001").solutions[first_solution_id]
    if updated_solution.alias == "updated_simple_lens":
        print("✅ Successfully updated alias to 'updated_simple_lens'")
    else:
        print("❌ Alias update failed: expected 'updated_simple_lens', got '" + updated_solution.alias + "'")

    # Check that the alias lookup table was updated by reloading the submission
    # This ensures we get the fresh lookup table after the edit operation
    sub_final = load(str(project_dir))
    final_alias_lookup = sub_final._build_alias_lookup()

    # Check that the specific solution's alias was updated correctly
    old_alias_key = "EVENT001 " + original_alias
    new_alias_key = "EVENT001 updated_simple_lens"

    # The old alias key should not map to our edited solution
    if old_alias_key in final_alias_lookup:
        if final_alias_lookup[old_alias_key] == first_solution_id:
            assert False, (
                "Old alias '" + old_alias_key + "' still maps to edited solution " + first_solution_id[:8] + "..."
            )
        else:
            print("✅ Old alias '" + old_alias_key + "' exists but maps to different solution (this is correct)")

    # The new alias key should map to our edited solution
    assert new_alias_key in final_alias_lookup, "New alias '" + new_alias_key + "' not added to lookup table"
    assert final_alias_lookup[new_alias_key] == first_solution_id, (
        "New alias '" + new_alias_key + "' maps to wrong solution"
    )

    print("✅ Alias lookup table properly updated")


if __name__ == "__main__":
    main()
