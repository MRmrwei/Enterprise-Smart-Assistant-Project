package models

import (
	"gorm.io/plugin/soft_delete"
)

type BaseModel struct {
	ID        uint `gorm:"primarykey"`
	CreatedAt int64
	UpdatedAt int64
	DeletedAt soft_delete.DeletedAt
}
