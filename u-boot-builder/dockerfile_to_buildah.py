#!/usr/bin/python3

import sys
import os

def dockerfile_to_buildah(dockerfile_path):
    with open(dockerfile_path) as f:
        dockerfile_lines = f.readlines()

    buildah_lines = []
    container = None
    convert_copy = False
    for line in dockerfile_lines:
        if line.startswith('FROM ') and not 'AS exporter' in line:
            image = line.split(' ')[1].strip()
            container = f'$container'
            buildah_lines.append(f'container=$(buildah from {image})\n')
        elif line.startswith('RUN '):
            command = line.split(' ', 1)[1].strip()
            buildah_lines.append(f'buildah run {container} {command}\n')
        elif line.startswith('COPY '):
            if 'qemu-aarch64-static' in line:
                continue
            source, dest = line.split()[1:3]
            buildah_lines.append(f'buildah copy $container {source} {dest}\n')
        elif line.startswith('CMD '):
            command = line.split(' ', 1)[1].strip()
            buildah_lines.append(f'buildah config --cmd "{command}" {container}\n')
        elif line.startswith('ENTRYPOINT '):
            command = line.split(' ', 1)[1].strip()
            buildah_lines.append(f'buildah config --entrypoint "{command}" {container}\n')
        elif line.startswith('ENV '):
            env_var, env_value = line.split(' ', 1)[1].strip().split('=')
            buildah_lines.append(f'buildah config --env {env_var}={env_value} {container}\n')
        elif line.startswith('LABEL '):
            labels = line.split(' ', 1)[1].strip()
            for label in labels.split(' '):
                key, value = label.split('=')
                buildah_lines.append(f'buildah config --label {key}="{value}" {container}\n')
        elif line.startswith('EXPOSE '):
            ports = line.split(' ')[1].strip()
            buildah_lines.append(f'buildah config --port {ports} {container}\n')
        elif line.startswith('WORKDIR '):
            workdir = line.split(' ')[1].strip()
            buildah_lines.append(f'buildah config --workingdir {workdir} {container}\n')
        elif line.startswith('FROM scratch AS exporter'):
            convert_copy = True
        elif convert_copy and not line.startswith('COPY --from=builder'):
            continue
        elif line.startswith('COPY --from=builder'):
            source, dest = line.split()[2:4]
            buildah_lines.append(f'cat << \'EOF\' >> copy-u-boot.sh\n')
            buildah_lines.append(f'#!/bin/sh\n')
            buildah_lines.append(f'mnt=$(buildah mount $container)\n')
            buildah_lines.append(f'cp $mnt{source} .{dest}\n')
            buildah_lines.append(f'buildah umount $container\n')
            buildah_lines.append(f'EOF\n')
            buildah_lines.append(f'chmod a+x copy-u-boot.sh\n')
            buildah_lines.append(f'buildah unshare ./copy-u-boot.sh\n')
            buildah_lines.append(f'rm ./copy-u-boot.sh\n')
        else:
            buildah_lines.append(line)

    buildah_lines.append(f'buildah rm $container\n')

    return ''.join(buildah_lines)



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python dockerfile_to_buildah.py [dockerfile_path]')
        sys.exit(1)

    dockerfile_path = sys.argv[1]
    print(dockerfile_path)
    buildah_script = dockerfile_to_buildah(dockerfile_path)

    # Get the filename without the extension
    filename, _ = os.path.splitext(dockerfile_path)

    # Write the Buildah script to a file with the same name as the Dockerfile
    with open(f'{filename}.sh', 'w') as f:
        f.write(buildah_script)

