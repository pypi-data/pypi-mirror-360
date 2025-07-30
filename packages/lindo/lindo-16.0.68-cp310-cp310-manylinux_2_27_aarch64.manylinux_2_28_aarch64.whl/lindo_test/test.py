def test_pyLindo_version():
    
    import lindo
    import numpy as np
    import os


    import lindo
    import numpy as np
    import os
    LS_IPARAM_VER_MAJOR = 16
    LS_IPARAM_VER_MINOR = 0

    pnErrorCode = np.array([-1],dtype=np.int32)
    licPath = os.getenv('LINDOAPI_HOME')+f"/license/lndapi{LS_IPARAM_VER_MAJOR}{LS_IPARAM_VER_MINOR}.lic" 
    try:
        LicenseKey = np.array([''],dtype='S1024')
        lindo.pyLSloadLicenseString(licPath,LicenseKey)
        pEnv = lindo.pyLScreateEnv(pnErrorCode,LicenseKey)
        lindo.pyLSdeleteEnv(pEnv)
        print(f"The Lindo API {LS_IPARAM_VER_MAJOR}.{LS_IPARAM_VER_MINOR} Python interface is working.")
    except lindo.LINDO_Exception as e:
        if(e.args[1] == lindo.LSERR_NO_VALID_LICENSE):
            print(f"{e.args[1]} => Unable to load license at {licPath}")
        else:
            print(e.args[0])