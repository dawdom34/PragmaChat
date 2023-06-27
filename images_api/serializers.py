from rest_framework import serializers

from .models import Images

from users.models import Account


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['user', 'image']

    def create(self, validated_data):
        user_id = validated_data.get('user')
        image = validated_data.get('image')

        new_image = Images.objects.create(user=user_id)
        new_image.image = image
        new_image.save()
        return new_image