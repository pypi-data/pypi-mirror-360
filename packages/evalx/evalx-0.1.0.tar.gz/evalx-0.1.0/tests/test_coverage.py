"""
Test coverage analysis and reporting for EvalX framework.

This module provides comprehensive test coverage analysis and reporting.
"""

import pytest
import coverage
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import importlib
import inspect


class CoverageAnalyzer:
    """Analyze test coverage for EvalX framework."""
    
    def __init__(self, source_dir: str = "evalx"):
        self.source_dir = Path(source_dir)
        self.coverage_data = {}
        self.uncovered_lines = {}
        self.coverage_report = {}
    
    def run_coverage_analysis(self) -> Dict:
        """Run comprehensive coverage analysis."""
        # Initialize coverage
        cov = coverage.Coverage(
            source=[str(self.source_dir)],
            omit=[
                "*/tests/*",
                "*/test_*",
                "*/__pycache__/*",
                "*/.*",
                "setup.py",
                "conftest.py"
            ]
        )
        
        # Start coverage
        cov.start()
        
        # Run tests
        pytest.main([
            str(self.source_dir.parent / "tests"),
            "--tb=short",
            "-v"
        ])
        
        # Stop coverage
        cov.stop()
        cov.save()
        
        # Generate report
        self.coverage_report = self._generate_coverage_report(cov)
        
        return self.coverage_report
    
    def _generate_coverage_report(self, cov: coverage.Coverage) -> Dict:
        """Generate detailed coverage report."""
        report = {
            "overall": {},
            "by_module": {},
            "by_category": {},
            "uncovered_lines": {},
            "missing_tests": []
        }
        
        # Get overall coverage
        total_lines = 0
        covered_lines = 0
        
        for file_path in cov.get_data().measured_files():
            if self.source_dir.name in file_path:
                analysis = cov.analysis2(file_path)
                filename = analysis[0]
                executed_lines = analysis[1]
                missing_lines = analysis[3]
                
                total_file_lines = len(executed_lines) + len(missing_lines)
                covered_file_lines = len(executed_lines)
                
                total_lines += total_file_lines
                covered_lines += covered_file_lines
                
                # Store module-level data
                module_name = self._get_module_name(filename)
                report["by_module"][module_name] = {
                    "filename": filename,
                    "total_lines": total_file_lines,
                    "covered_lines": covered_file_lines,
                    "coverage_percent": (covered_file_lines / total_file_lines * 100) if total_file_lines > 0 else 0,
                    "missing_lines": missing_lines
                }
                
                if missing_lines:
                    report["uncovered_lines"][module_name] = missing_lines
        
        # Overall coverage
        overall_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
        report["overall"] = {
            "total_lines": total_lines,
            "covered_lines": covered_lines,
            "coverage_percent": overall_coverage
        }
        
        # Category-based coverage
        report["by_category"] = self._categorize_coverage(report["by_module"])
        
        # Find missing tests
        report["missing_tests"] = self._find_missing_tests()
        
        return report
    
    def _get_module_name(self, filename: str) -> str:
        """Extract module name from filename."""
        path = Path(filename)
        if self.source_dir.name in path.parts:
            # Find the index of the source directory
            parts = path.parts
            source_index = parts.index(self.source_dir.name)
            
            # Get relative path from source directory
            relative_parts = parts[source_index:]
            
            # Convert to module name
            if relative_parts[-1] == "__init__.py":
                module_parts = relative_parts[:-1]
            else:
                module_parts = relative_parts[:-1] + (relative_parts[-1].replace(".py", ""),)
            
            return ".".join(module_parts)
        
        return path.stem
    
    def _categorize_coverage(self, by_module: Dict) -> Dict:
        """Categorize coverage by component type."""
        categories = {
            "core": [],
            "metrics": [],
            "agents": [],
            "utils": [],
            "validation": [],
            "other": []
        }
        
        for module_name, data in by_module.items():
            if "core" in module_name:
                categories["core"].append(data)
            elif "metrics" in module_name:
                categories["metrics"].append(data)
            elif "agents" in module_name:
                categories["agents"].append(data)
            elif "utils" in module_name:
                categories["utils"].append(data)
            elif "validation" in module_name:
                categories["validation"].append(data)
            else:
                categories["other"].append(data)
        
        # Calculate category averages
        category_summary = {}
        for category, modules in categories.items():
            if modules:
                total_lines = sum(m["total_lines"] for m in modules)
                covered_lines = sum(m["covered_lines"] for m in modules)
                avg_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
                
                category_summary[category] = {
                    "modules": len(modules),
                    "total_lines": total_lines,
                    "covered_lines": covered_lines,
                    "coverage_percent": avg_coverage,
                    "module_details": modules
                }
        
        return category_summary
    
    def _find_missing_tests(self) -> List[str]:
        """Find components that may be missing tests."""
        missing_tests = []
        
        # Check for test files
        test_dir = self.source_dir.parent / "tests"
        existing_test_files = set()
        
        if test_dir.exists():
            for test_file in test_dir.glob("test_*.py"):
                existing_test_files.add(test_file.stem)
        
        # Check source files
        for py_file in self.source_dir.rglob("*.py"):
            if py_file.name != "__init__.py":
                relative_path = py_file.relative_to(self.source_dir)
                module_path = str(relative_path).replace("/", "_").replace(".py", "")
                expected_test_file = f"test_{module_path}"
                
                if expected_test_file not in existing_test_files:
                    missing_tests.append(str(relative_path))
        
        return missing_tests
    
    def generate_html_report(self, output_file: str = "coverage_report.html"):
        """Generate HTML coverage report."""
        if not self.coverage_report:
            self.run_coverage_analysis()
        
        html_content = self._generate_html_content()
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        return output_file
    
    def _generate_html_content(self) -> str:
        """Generate HTML content for coverage report."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>EvalX Test Coverage Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
                .section { margin: 20px 0; }
                .coverage-bar { 
                    width: 100%; 
                    height: 20px; 
                    background-color: #f0f0f0; 
                    border-radius: 10px; 
                    overflow: hidden;
                }
                .coverage-fill { 
                    height: 100%; 
                    background-color: #4CAF50; 
                    transition: width 0.3s ease;
                }
                .low-coverage { background-color: #f44336; }
                .medium-coverage { background-color: #ff9800; }
                .high-coverage { background-color: #4CAF50; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .missing-lines { color: #f44336; font-family: monospace; }
                .good-coverage { color: #4CAF50; font-weight: bold; }
                .poor-coverage { color: #f44336; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>EvalX Test Coverage Report</h1>
                <h2>Overall Coverage: {overall_percent:.1f}%</h2>
                <div class="coverage-bar">
                    <div class="coverage-fill {overall_class}" style="width: {overall_percent}%"></div>
                </div>
                <p>Total Lines: {total_lines} | Covered Lines: {covered_lines}</p>
            </div>
        """.format(
            overall_percent=self.coverage_report["overall"]["coverage_percent"],
            overall_class=self._get_coverage_class(self.coverage_report["overall"]["coverage_percent"]),
            total_lines=self.coverage_report["overall"]["total_lines"],
            covered_lines=self.coverage_report["overall"]["covered_lines"]
        )
        
        # Add category section
        html += """
            <div class="section">
                <h3>Coverage by Category</h3>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Modules</th>
                        <th>Total Lines</th>
                        <th>Covered Lines</th>
                        <th>Coverage %</th>
                        <th>Coverage Bar</th>
                    </tr>
        """
        
        for category, data in self.coverage_report["by_category"].items():
            coverage_class = self._get_coverage_class(data["coverage_percent"])
            html += f"""
                    <tr>
                        <td>{category.title()}</td>
                        <td>{data["modules"]}</td>
                        <td>{data["total_lines"]}</td>
                        <td>{data["covered_lines"]}</td>
                        <td class="{coverage_class}">{data["coverage_percent"]:.1f}%</td>
                        <td>
                            <div class="coverage-bar">
                                <div class="coverage-fill {coverage_class}" style="width: {data["coverage_percent"]}%"></div>
                            </div>
                        </td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
        """
        
        # Add module details
        html += """
            <div class="section">
                <h3>Coverage by Module</h3>
                <table>
                    <tr>
                        <th>Module</th>
                        <th>Total Lines</th>
                        <th>Covered Lines</th>
                        <th>Coverage %</th>
                        <th>Missing Lines</th>
                    </tr>
        """
        
        for module_name, data in self.coverage_report["by_module"].items():
            coverage_class = self._get_coverage_class(data["coverage_percent"])
            missing_lines = ", ".join(map(str, data["missing_lines"])) if data["missing_lines"] else "None"
            
            html += f"""
                    <tr>
                        <td>{module_name}</td>
                        <td>{data["total_lines"]}</td>
                        <td>{data["covered_lines"]}</td>
                        <td class="{coverage_class}">{data["coverage_percent"]:.1f}%</td>
                        <td class="missing-lines">{missing_lines}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
        """
        
        # Add missing tests section
        if self.coverage_report["missing_tests"]:
            html += """
                <div class="section">
                    <h3>Missing Test Files</h3>
                    <ul>
            """
            
            for missing_test in self.coverage_report["missing_tests"]:
                html += f"<li>{missing_test}</li>"
            
            html += """
                    </ul>
                </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def _get_coverage_class(self, coverage_percent: float) -> str:
        """Get CSS class based on coverage percentage."""
        if coverage_percent >= 90:
            return "high-coverage"
        elif coverage_percent >= 70:
            return "medium-coverage"
        else:
            return "low-coverage"
    
    def print_coverage_summary(self):
        """Print coverage summary to console."""
        if not self.coverage_report:
            self.run_coverage_analysis()
        
        print("\n" + "="*60)
        print("EVALX TEST COVERAGE SUMMARY")
        print("="*60)
        
        # Overall coverage
        overall = self.coverage_report["overall"]
        print(f"Overall Coverage: {overall['coverage_percent']:.1f}%")
        print(f"Total Lines: {overall['total_lines']}")
        print(f"Covered Lines: {overall['covered_lines']}")
        print()
        
        # Category coverage
        print("Coverage by Category:")
        print("-" * 40)
        for category, data in self.coverage_report["by_category"].items():
            print(f"{category.title():15} {data['coverage_percent']:6.1f}% ({data['covered_lines']}/{data['total_lines']} lines)")
        print()
        
        # Low coverage modules
        print("Modules with Low Coverage (<70%):")
        print("-" * 40)
        low_coverage_modules = [
            (name, data) for name, data in self.coverage_report["by_module"].items()
            if data["coverage_percent"] < 70
        ]
        
        if low_coverage_modules:
            for module_name, data in low_coverage_modules:
                print(f"{module_name:30} {data['coverage_percent']:6.1f}%")
        else:
            print("None - All modules have ≥70% coverage!")
        print()
        
        # Missing tests
        if self.coverage_report["missing_tests"]:
            print("Missing Test Files:")
            print("-" * 40)
            for missing_test in self.coverage_report["missing_tests"]:
                print(f"  {missing_test}")
        else:
            print("All modules have corresponding test files!")
        
        print("="*60)
    
    def get_coverage_metrics(self) -> Dict:
        """Get coverage metrics for CI/CD integration."""
        if not self.coverage_report:
            self.run_coverage_analysis()
        
        metrics = {
            "overall_coverage": self.coverage_report["overall"]["coverage_percent"],
            "total_lines": self.coverage_report["overall"]["total_lines"],
            "covered_lines": self.coverage_report["overall"]["covered_lines"],
            "categories": {},
            "low_coverage_modules": [],
            "missing_tests": len(self.coverage_report["missing_tests"]),
            "coverage_grade": self._get_coverage_grade(self.coverage_report["overall"]["coverage_percent"])
        }
        
        # Category metrics
        for category, data in self.coverage_report["by_category"].items():
            metrics["categories"][category] = {
                "coverage": data["coverage_percent"],
                "modules": data["modules"]
            }
        
        # Low coverage modules
        for module_name, data in self.coverage_report["by_module"].items():
            if data["coverage_percent"] < 70:
                metrics["low_coverage_modules"].append({
                    "module": module_name,
                    "coverage": data["coverage_percent"]
                })
        
        return metrics
    
    def _get_coverage_grade(self, coverage_percent: float) -> str:
        """Get letter grade for coverage percentage."""
        if coverage_percent >= 95:
            return "A+"
        elif coverage_percent >= 90:
            return "A"
        elif coverage_percent >= 85:
            return "B+"
        elif coverage_percent >= 80:
            return "B"
        elif coverage_percent >= 75:
            return "C+"
        elif coverage_percent >= 70:
            return "C"
        elif coverage_percent >= 60:
            return "D"
        else:
            return "F"


def test_coverage_analysis():
    """Test the coverage analysis functionality."""
    analyzer = CoverageAnalyzer()
    
    # Run analysis
    report = analyzer.run_coverage_analysis()
    
    # Basic assertions
    assert "overall" in report
    assert "by_module" in report
    assert "by_category" in report
    
    # Check that we have reasonable coverage
    overall_coverage = report["overall"]["coverage_percent"]
    assert overall_coverage >= 0  # At least some coverage
    
    # Check that main categories are present
    expected_categories = ["core", "metrics", "agents", "utils"]
    for category in expected_categories:
        if category in report["by_category"]:
            assert report["by_category"][category]["coverage_percent"] >= 0


def test_coverage_reporting():
    """Test coverage reporting functionality."""
    analyzer = CoverageAnalyzer()
    
    # Generate HTML report
    html_file = analyzer.generate_html_report("test_coverage_report.html")
    
    # Check that file was created
    assert os.path.exists(html_file)
    
    # Check that file has content
    with open(html_file, 'r') as f:
        content = f.read()
        assert "EvalX Test Coverage Report" in content
        assert "Overall Coverage" in content
    
    # Clean up
    os.remove(html_file)


def test_coverage_metrics():
    """Test coverage metrics extraction."""
    analyzer = CoverageAnalyzer()
    
    metrics = analyzer.get_coverage_metrics()
    
    # Check required metrics
    assert "overall_coverage" in metrics
    assert "total_lines" in metrics
    assert "covered_lines" in metrics
    assert "categories" in metrics
    assert "coverage_grade" in metrics
    
    # Check that metrics are reasonable
    assert 0 <= metrics["overall_coverage"] <= 100
    assert metrics["total_lines"] > 0
    assert metrics["covered_lines"] >= 0
    assert metrics["coverage_grade"] in ["A+", "A", "B+", "B", "C+", "C", "D", "F"]


if __name__ == "__main__":
    # Run coverage analysis
    analyzer = CoverageAnalyzer()
    analyzer.print_coverage_summary()
    
    # Generate HTML report
    html_file = analyzer.generate_html_report()
    print(f"\nHTML report generated: {html_file}")
    
    # Get metrics for CI/CD
    metrics = analyzer.get_coverage_metrics()
    print(f"\nCoverage Grade: {metrics['coverage_grade']}")
    print(f"Overall Coverage: {metrics['overall_coverage']:.1f}%") 