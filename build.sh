cargo build --release
rm -rf /home/okayu/bancho.py/tools/libokayu_pp_ffi.so
rm -rf /home/okayu/bancho.py/app/usecases/libokayu_pp_ffi.so
cp -r /home/okayu/treekitora/akatsuki-pp-ffi/target/release/libokayu_pp_ffi.so /home/okayu/bancho.py/tools/
cp -r /home/okayu/treekitora/akatsuki-pp-ffi/target/release/libokayu_pp_ffi.so /home/okayu/bancho.py/app/usecases/