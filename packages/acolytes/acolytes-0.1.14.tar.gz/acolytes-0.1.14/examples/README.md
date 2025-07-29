# ACOLYTE Configuration Examples

This directory contains example configuration files for ACOLYTE.

## Files

### `.acolyte.example`
Example of the main ACOLYTE configuration file. This file is NOT used directly - it's just for reference.
Actual configuration is stored in `~/.acolyte/projects/{project_id}/config.yaml`

### `.acolyte.project.example`
Example of the project marker file that identifies a directory as an ACOLYTE-managed project.
Contains only the project ID and is about 200 bytes.

### `.acolyteignore.example`
Example of patterns to ignore during code indexing, similar to `.gitignore`.
Users can create their own `.acolyteignore` in their project root.

## Usage

To use these examples:
1. Copy the example file you need
2. Remove the `.example` extension
3. Modify the content according to your needs
4. Place it in the appropriate location
