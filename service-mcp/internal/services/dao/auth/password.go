package auth

type Password interface {
	Encrypt(pwd string) (string, error)
	Verify(pwd, hash string) bool
}
