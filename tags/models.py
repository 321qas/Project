# tags/models.py
from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

    def user_count(self):
        # 역참조를 이용한 실시간 카운트 반환 (User에서 ManyToMany 선언했을 때)
        return self.user_set.count()
        # 사용 예시
        # music_tag = Tag.objects.get(name='음악')
        # print(music_tag.user_count())   # 출력 결과 = 3
