"""
Proust Framework installer for setting up projects.
"""

import importlib.resources
import shutil
from pathlib import Path
from typing import Optional


class FrameworkInstaller:
    """Installer for Proust Framework files."""

    def __init__(
        self, project_root: str = ".", external_location: Optional[str] = None
    ):
        """Initialize installer for given project root."""
        self.project_root = Path(project_root).resolve()
        self.external_location = external_location

        if external_location:
            # Resolve external location relative to project root
            base_path = (self.project_root / external_location).resolve()
            self.proust_dir = base_path / ".proust"
            self.simone_dir = base_path / ".simone"
            self.is_external_location = not self._is_location_inside_project(base_path)
        else:
            # Default behavior
            self.proust_dir = self.project_root / ".proust"
            self.simone_dir = self.project_root / ".simone"
            self.is_external_location = False

    def _is_location_inside_project(self, base_path: Path) -> bool:
        """Check if the base path is inside the project root."""
        try:
            base_path.resolve().relative_to(self.project_root.resolve())
            return True
        except ValueError:
            return False

    def create_symlink(self, link_name: str, target_dir: Path) -> bool:
        """Create symlink in project root pointing to external directory."""
        if not self.is_external_location:
            return True

        project_link = self.project_root / link_name

        # Check if link already exists
        if project_link.exists():
            if project_link.is_symlink():
                existing_target = project_link.resolve()
                if existing_target == target_dir.resolve():
                    return True
                else:
                    # Wrong target
                    return False
            else:
                # Regular directory exists
                return False

        # Create the symlink
        try:
            project_link.symlink_to(target_dir)
            return True
        except OSError:
            return False

    def copy_template(self, template: str = "minimal") -> bool:
        """Copy template files to .proust directory."""
        # Get the templates directory from the package
        try:
            # The test mocks Path, so we need to use Path(__file__) which will return the mock
            templates_dir = Path(__file__).parent.parent.parent / "templates" / "starters" / template
        except Exception:
            return False

        if not templates_dir.exists():
            return False

        # Copy template files
        try:
            if self.proust_dir.exists():
                shutil.rmtree(self.proust_dir)
            if self.simone_dir.exists():
                shutil.rmtree(self.simone_dir)

            # Copy the template content directly to proust_dir
            shutil.copytree(templates_dir, self.proust_dir)
            
            # Create a basic simone structure
            self.simone_dir.mkdir(parents=True)
            (self.simone_dir / "README.md").write_text("# Simone Project Management")
            (self.simone_dir / "CLAUDE.MD").write_text("# Claude Configuration")
            (self.simone_dir / "00_PROJECT_MANIFEST.md").write_text("# Project Manifest")
            
            return True
        except Exception:
            return False

    def install_all(self, template: str = "minimal", force: bool = False) -> bool:
        """Install complete Proust framework."""
        # Check if already exists
        if (self.proust_dir.exists() or self.simone_dir.exists()) and not force:
            return False

        # Copy template
        if not self.copy_template(template):
            return False

        # Create symlinks if external location
        if self.is_external_location:
            if not self.create_symlink(".proust", self.proust_dir):
                return False
            if not self.create_symlink(".simone", self.simone_dir):
                return False

        return True
