from rest_framework import serializers

from nkunyim_iam.models import App, Nat, User



class AppSerializer(serializers.ModelSerializer):

    class Meta:
        model = App
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class NatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Nat
        fields = '__all__'

