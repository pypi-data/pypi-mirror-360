from asanak_sms_client import AsanakSMSClient

def test_send_sms():
    client = AsanakSMSClient("test", "pass")
    try:
        response = client.send_sms("9821X", "0912000000", "کد تست 1234")
        assert "meta" in response
    except Exception as e:
        assert False, str(e)
