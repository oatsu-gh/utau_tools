REM reclsit2region.py��exe�ɂ��Ĕz�z�pzip�ɂ���o�b�`

mkdir �^�����X�g���烊�[�W����CSV�𐶐�����c�[��
copy /Y reclist2region.py �^�����X�g���烊�[�W����CSV�𐶐�����c�[��\reclist2region.py
copy /Y README.md �^�����X�g���烊�[�W����CSV�𐶐�����c�[��\readme.txt
cd �^�����X�g���烊�[�W����CSV�𐶐�����c�[��

pyinstaller.exe reclist2region.py --onefile --clean --exclude-module readme.txt

move /Y dist\reclist2region.exe reclist2region.exe
rmdir /s /q dist, build, __pycache__
del /q reclist2region.spec, reclist2region.py
cd ..

powershell compress-archive -Force �^�����X�g���烊�[�W����CSV�𐶐�����c�[�� �^�����X�g���烊�[�W����CSV�𐶐�����c�[��.zip
rmdir /s /q �^�����X�g���烊�[�W����CSV�𐶐�����c�[��
