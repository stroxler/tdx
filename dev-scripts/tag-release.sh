#!/usr/bin/env bash
version="v$(python setup.py --version)"
git tag -a "${version}" -m "Release ${version}" 
git push origin --tags
