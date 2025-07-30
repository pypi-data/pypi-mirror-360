# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     Javier Sanchez
# *
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************


from os.path import exists
import traceback

from pyworkflow.tests import BaseTest, setupTestProject
import pwem.protocols as emprot
from cryoten.protocols.protocol_cryoten import CryotenPrefixEnhace  # Adjusted import path

class TestCryoten(BaseTest):
    @classmethod
    def setUpClass(cls):
        try:
            setupTestProject(cls)
        except Exception as e:
            print("Error during setupTestProject:")
            traceback.print_exc()
            raise e

    def test_CryotenPrefixEnhace(self):
        try:
            # Step 1: Import volume from EMDB
            EMDBiD = 51521
            args = {
                'importFrom': emprot.ProtImportVolumes.IMPORT_FROM_EMDB,
                'emdbId': EMDBiD,
            }

            prot = self.newProtocol(emprot.ProtImportVolumes, **args)
            prot.setObjLabel('import vol')
            self.launchProtocol(prot)
            vol = prot.outputVolume

            # Step 2: Run CryotenPrefixEnhace protocol
            args = {
                'inputVolume': vol,
                'useGpu': True,
                'gpuList': "0",
            }
            protCryoten = self.newProtocol(CryotenPrefixEnhace, **args)
            protCryoten.setObjLabel('cryoten enhance')
            self.launchProtocol(protCryoten)

            # Step 3: Check results
            self.assertTrue(protCryoten.outputFilePath is not None, "Output file path is None")
            outputFilePath = protCryoten.outputFilePath.get()
            print(f"Output file path: {outputFilePath}")
            self.assertTrue(exists(outputFilePath), f"Output file does not exist: {outputFilePath}")
        except Exception as e:
            print("Error during test_CryotenPrefixEnhace:")
            traceback.print_exc()
            raise e

# Example of running the test
if __name__ == '__main__':
    import unittest
    unittest.main()