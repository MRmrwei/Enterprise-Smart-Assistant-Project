package auth

import (
	"ai/service-mcp/internal/services/dao/auth"
	"golang.org/x/crypto/bcrypt"
)

type PasswordImpl struct {
}

func NewPasswordImpl() auth.Password {
	return &PasswordImpl{}
}
func (this *PasswordImpl) Encrypt(pwd string) (string, error) {
	// bcrypt.DefaultCost 是默认的成本因子，值越高计算越慢，推荐 10 左右
	bytes, err := bcrypt.GenerateFromPassword([]byte(pwd), bcrypt.DefaultCost)
	return string(bytes), err
}

// Verify 验证原始密码是否与存储的哈希密码匹配
func (this *PasswordImpl) Verify(pwd, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(pwd))
	return err == nil
}
