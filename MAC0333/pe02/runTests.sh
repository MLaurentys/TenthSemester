set -x
rm -v ../tests/original/directory/mir*
rm -rf ../tests/copy
cp -r ../tests/original ../tests/copy
python3 mir.py -@encodes.lst ../tests/copy/directory
touch ../tests/copy/directory/arq0.txt
rm ../tests/copy/directory/arq1.txt
python3 mir.py -A ../tests/copy/directory
python3 mirs.py -t 5 -r ".ã$" ../tests/copy/directory
