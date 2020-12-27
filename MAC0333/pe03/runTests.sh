
set -x
rm -v ../tests/original/directory/mir*
rm -rf ../tests/copy
cp -r ../tests/original ../tests/copy
python3 mir.py -@encodes.lst ../tests/copy/directory
touch ../tests/copy/directory/arq0.txt
rm ../tests/copy/directory/arq1.txt
python3 mir.py -A ../tests/copy/directory
python3 mirs.py -r ".*Ã£$" ../tests/copy/directory
python3 mirs.py ../tests/copy/directory/ prêmio internacional ime
python3 mirs.py -o 1 ../tests/copy/directory/ prêmio internacional ime
python3 mirs.py -o 2 ../tests/copy/directory/ prêmio internacional ime
python3 mirs.py -o 3 ../tests/copy/directory/ prêmio internacional ime
python3 mirs.py -o 4 ../tests/copy/directory/ prêmio internacional ime
python3 mirs.py -v -o 3 ../tests/copy/directory/ prêmio internacional ime
python3 mirs.py -v -o 4 ../tests/copy/directory/ prêmio internacional ime
