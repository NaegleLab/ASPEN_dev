import unittest
from mock import patch,call,mock_open
from topolenum import topolenum as te


@patch('tempfile.NamedTemporaryFile')
class TestFIFOfileBaseClassTMPFILEclass(unittest.TestCase):
  
  def setUp(self):
    self.TMPFILE = te.FIFOfile.TMPFILE
    self.TMPFILE.init_class(mode='b',wbuf=0,rbuf=0,suffix='',delete=True,
                            dir='/dummy/path',check_freq=5)
  
  def test_instance_counting_and_file_creation_and_naming(self,patched_NTF):
    
    tmpfile_instance1 = self.TMPFILE()
    self.assertEqual(tmpfile_instance1.instcount,self.TMPFILE.instcount)
    self.assertEqual(self.TMPFILE.instcount,1)
    patched_NTF.assert_called_with('rb',0,suffix='',prefix='FIFOfile001_',
                                   dir='/dummy/path',delete=True)
    self.TMPFILE()
    self.assertEqual(self.TMPFILE.instcount,2)
    patched_NTF.assert_called_with('rb',0,suffix='',prefix='FIFOfile002_',
                                   dir='/dummy/path',delete=True)
  
  def test_spooling_and_file_spool_interaction(self,patched_NTF):
    self.assertFalse(hasattr(self.TMPFILE,'file_spool'))
    self.TMPFILE.start_spooling()
    self.assertTrue(hasattr(self.TMPFILE,'file_spool'))
    self.assertEqual(len(self.TMPFILE.file_spool),0)
    tmpfile_instance = self.TMPFILE.spool()
    self.assertEqual(len(self.TMPFILE.file_spool),1)
    self.assertIs(tmpfile_instance,self.TMPFILE.pop_from_spool())
    self.assertEqual(len(self.TMPFILE.file_spool),0)
    self.assertIs(None,self.TMPFILE.pop_from_spool())
  
  def test_writing_handle(self,patched_NTF):
    tmpfile_instance = self.TMPFILE()
    self.assertFalse(hasattr(tmpfile_instance,'wh'))
    with patch('__builtin__.open',mock_open(),create=True) as patched_open:
      tmpfile_instance.open()
      patched_open.assert_called_once_with(patched_NTF.return_value.name,'wb',0)
      self.assertTrue(hasattr(tmpfile_instance,'wh'))
      self.assertIs(tmpfile_instance.wh,patched_open.return_value)
    tmpfile_instance.close()
    tmpfile_instance.wh.close.assert_called_once_with()
  
  @patch('os.path.getsize',side_effect=[10,20])
  def test_size_checking(self,patched_getsize,patched_NTF):
    tmpfile_instance = self.TMPFILE()
    self.assertSequenceEqual([tmpfile_instance.size for i in xrange(6)],
                             [0.0,0.0,0.0,0.0,0.0,0.0])
    patched_getsize.assert_not_called()
    self.assertEqual(tmpfile_instance.size,10)
    patched_getsize.assert_called_once_with(patched_NTF.return_value.name)
    self.assertSequenceEqual([tmpfile_instance.size for i in xrange(6)],
                             [10.0,10.0,10.0,10.0,10.0,10.0])
    patched_getsize.assert_called_once_with(patched_NTF.return_value.name)
    self.assertEqual(tmpfile_instance.size,20)
    self.assertSequenceEqual(patched_getsize.call_args_list,
                             [call(patched_NTF.return_value.name),
                              call(patched_NTF.return_value.name)],list)
  
  @patch('os.path.exists',return_value=False)
  def test_file_discarding(self,patched_exists,patched_NTF):
    tmpfile_instance = self.TMPFILE()
    self.assertIs(tmpfile_instance.rh,patched_NTF.return_value)
    tmpfile_instance.discard()
    tmpfile_instance.rh.close.assert_called_once_with()


if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
