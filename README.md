This repository contains a Python class that can be used to access files and
folders on Windows. It supports local drives or SMB network shares, reading and
writing files inside zip files, Unicode names and very long paths.

It is a continuation of my `mFileSystem` and `mFileSystem2` Python scripts that
offered similar functionality. `cFileSystemItem` is intended to be a replacement
for both by offering a more unified API and more features, specifically support
for accessing files within .zip files.
