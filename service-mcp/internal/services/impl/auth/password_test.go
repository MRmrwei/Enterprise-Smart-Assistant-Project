package auth

import "testing"

func TestPasswordImpl_Encrypt(t *testing.T) {
	pwd, _ := NewPasswordImpl().Encrypt("123456")
	apwd, _ := NewPasswordImpl().Encrypt("admin")
	t.Logf("普通密码：%s", pwd)
	t.Logf("管理员密码：%s", apwd)
}

func TestPasswordImpl_Verify(t *testing.T) {
	pwd := "123456"
	hashPwd := "$2a$10$ATUOasb1grHNVIpOy2PzXOfvkg8r8OW83juevhkIVLawkPBDoAtMy"
	t.Log(NewPasswordImpl().Verify(pwd, hashPwd))

}
