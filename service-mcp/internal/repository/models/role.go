package models

type RoleModel struct {
	BaseModel
	Name   string
	Weight int64
	Code   string
}

func (r *RoleModel) TableName() string {
	return "ai_role"
}
