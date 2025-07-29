from setuptools import setup
from setuptools.command.install_scripts import install_scripts
import os
import re

class InstallScriptsWithArgcomplete(install_scripts):
    def run(self):
        # Run the original install_scripts
        super().run()

        # Add PYTHON_ARGCOMPLETE_OK to slowarg script
        for script in self.outfiles:
            if os.path.basename(script) == 'slowarg':
                with open(script, 'r') as f:
                    content = f.read()

                # Check if marker already exists
                if '# PYTHON_ARGCOMPLETE_OK' not in content:
                    # Add marker after shebang
                    content = re.sub(
                        r'(#!/.*\n)',
                        r'\1# PYTHON_ARGCOMPLETE_OK\n',
                        content,
                        count=1
                    )

                    with open(script, 'w') as f:
                        f.write(content)
                    print(f"Added PYTHON_ARGCOMPLETE_OK marker to {script}")

if __name__ == '__main__':
    setup(
        cmdclass={
            'install_scripts': InstallScriptsWithArgcomplete,
        }
    )
