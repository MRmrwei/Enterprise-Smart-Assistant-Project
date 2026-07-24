package models

type UserModel struct {
	BaseModel
	Password string
	Account  string
	Nickname string
}

func (this *UserModel) TableName() string {
	return "ai_user"
}
