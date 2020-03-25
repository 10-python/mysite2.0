from django.test import TestCase,Client
class SendViewTestCasel(TestCase):
    def test_user_register(self):
        # 定义测试客户端
        self.client=Client()
        # 请求访问注册页
        rep=self.client.get('/user/register_ajax/')
        self.assertEqual(rep.status_code,200)
        self.assertContains(rep,'cotent')
    def test_user_exist(self):
        rep=self.client.get('/user/check_username/?username=''')
        self.assertEqual(rep.status_code,200)
        self.assertIs(rep.rep,{'count':1})
    def test_user_login(self):
        rep=self.client.get('/user/login_for_modal/')
        self.assertEqual(rep.status_code,200)
        login_status=self.client.post('/user/login_for_modal/',{'username':'0001','password':'12345678'})
        self.assertEqual(login_status.status_code,200)
    def test_user_info(self):
        rep=self.client.get('/user/user_info/')
        self.assertEqual(rep.status_code,401)

