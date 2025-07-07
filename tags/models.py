from django.db import models

class Tag(models.Model):                                    # 관심 태그
    name = models.CharField(max_length=30, unique=True)
    # 문화예술, 전통역사, 자연생태, 지역특산물, 먹거리/푸드, 음악/공연, 체험/참여, 봄, 여름, 가을, 겨울, 가족, 어린이, 청소년, 가족, 성인, 어르신, 전연령 / 총 19개

    def __str__(self):
        return self.name

    def user_count(self):                                   # 유저 수
        return self.user_set.count()
