from django.db import models


class EndPose(models.Model):
    end_pose_id = models.CharField(primary_key=True, max_length=50)
    type = models.BinaryField(max_length=30)
    x_mean = models.FloatField(default=0.00)
    y_min = models.FloatField(default=0.00)
    duration = models.FloatField(default=0.00)

    def __str__(self):
        return self.end_pose_id


class StartPose(models.Model):
    start_pose_id = models.CharField(primary_key=True, max_length=50)
    type = models.BinaryField(max_length=30)
    x_mean = models.FloatField(default=0.00)
    y_min = models.FloatField(default=0.00)
    duration = models.FloatField(default=0.00)

    # end_pose_id = models.ForeignKey(EndPose, on_delete=models.CASCADE)

    def __str__(self):
        return self.start_pose_id
