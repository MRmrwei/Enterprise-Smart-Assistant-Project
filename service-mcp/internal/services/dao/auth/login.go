package auth

import "context"

type Login interface {
	Login(ctx context.Context, account string, password string) (string, error)
}
