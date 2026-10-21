"""Non-mutating preflight for locally supplied CodeWarrior/Kamek commands."""
import argparse
import shlex
import shutil
import sys

p = argparse.ArgumentParser()
p.add_argument('--cc', required=True)
p.add_argument('--assembler', required=True)
p.add_argument('--linker', required=True)
args = p.parse_args()
missing = []
for name, command in vars(args).items():
    parts = shlex.split(command)
    if not parts or shutil.which(parts[0]) is None:
        missing.append(f'{name}: {command}')
if missing:
    print('BUILD BLOCKED: required build commands are unavailable:', file=sys.stderr)
    print('\n'.join('  ' + item for item in missing), file=sys.stderr)
    print('Set CC, AS and KAMEK in .env to your supplied toolchain commands.', file=sys.stderr)
    sys.exit(1)
print('Build commands found (this does not verify compiler/linker compatibility).')
