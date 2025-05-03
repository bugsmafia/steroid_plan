from rest_framework import serializers
from .models import (
    User, Subscription,
    DrugGroup, Drug, SideEffect,
    DrugSideEffect, IntakeDuration,
    DrugCompatibility, EtherType,
    ReceptionMethod, DrugReception,
    DrugInfo, DecayFormula,
    Course, CourseDose, BloodAnalysis,
    CourseDrugSchedule
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','role','sex','age','weight_kg','experience']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id','user','start_date','end_date','status','stripe_customer_id','stripe_subscription_id','auto_renewal']

class DrugGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugGroup
        fields = ['id','name']

class DrugSerializer(serializers.ModelSerializer):
    group = DrugGroupSerializer(read_only=True)
    group_id = serializers.PrimaryKeyRelatedField(queryset=DrugGroup.objects.all(), source='group', write_only=True)
    class Meta:
        model = Drug
        fields = ['id','name','group','group_id','sort', 'info', 'decay_formula']

class SideEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SideEffect
        fields = ['id','name']

class DrugSideEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugSideEffect
        fields = ['drug','effect','level']

class IntakeDurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntakeDuration
        fields = ['drug','min_duration_days','rec_duration_days','max_duration_days']

class DrugCompatibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugCompatibility
        fields = ['drug_a','drug_b','compatibility','reason']

class EtherTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtherType
        fields = ['id','drug','ether_type']

class ReceptionMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceptionMethod
        fields = ['id','method']

class DrugReceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugReception
        fields = ['drug','reception_method']

class DrugInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugInfo
        fields = ['drug','info','half_life_hours','elimination_hours']

class DecayFormulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecayFormula
        fields = ['drug','formula']

class BloodAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodAnalysis
        fields = ['id','user','analysis_date','testosterone','prolactin','liver_enzymes','comment','created_at']
        
class CourseDrugScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDrugSchedule
        fields = [
            'id',
            'drug',
            'D',           # доза теперь называется D
            'delta_t',     # вместо interval_h
            'day_of_week', # вместо weekday
            'dose_time',   # вместо dose_clock
        ]

class CourseDoseSerializer(serializers.ModelSerializer):
    drug = serializers.CharField(source='schedule.drug.name', read_only=True)
    class Meta:
        model = CourseDose
        fields = ('id','drug','dose_mg','intake_dt')

class CourseSerializer(serializers.ModelSerializer):
    drug_schedules = CourseDrugScheduleSerializer(many=True)
    doses          = CourseDoseSerializer(many=True, read_only=True)
    concentration  = serializers.JSONField(source='concentration_cache', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'name',
            'description',
            'start_time',   # теперь на курсе
            'T_total',      # теперь на курсе
            'drug_schedules',
            'doses',
            'concentration',
        ]


    def create(self, validated_data):
        schedules = validated_data.pop('drug_schedules', [])
        # user из контекста
        user = self.context['request'].user
        course = Course.objects.create(user=user, **validated_data)
        for sched in schedules:
            CourseDrugSchedule.objects.create(course=course, **sched)
        from .services import regenerate_course_schedule
        regenerate_course_schedule(course)
        return course

    def update(self, instance, validated_data):
        schedules = validated_data.pop('drug_schedules', None)
        # обновляем поля курса
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        if schedules is not None:
            # сброс и пересоздание расписания
            instance.drug_schedules.all().delete()
            for sched in schedules:
                CourseDrugSchedule.objects.create(course=instance, **sched)
            from .services import regenerate_course_schedule
            regenerate_course_schedule(instance)

        return instance