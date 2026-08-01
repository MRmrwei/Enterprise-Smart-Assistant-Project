package user

import (
	"ai/service-mcp/internal/repository/models"
	"context"
)

type UserDao interface {
	GetByAccount(ctx context.Context, account string) (*models.UserModel, error)
}
