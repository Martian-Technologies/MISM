import numpy as np

def move_outside_sphere(point, radius):
    if vecLength(point) < radius:
        return setVectorLength(point, radius)
    return point

def move_inside_sphere(point, radius):
    if not vecLength(point) < radius:
        return setVectorLength(point, radius)
    return point

def SSS(a,b,c,output):
    """Input the ABC of a tri and input the side name ('a','b','c') across from the angle you want"""
    if output == "a":
        return np.degrees(np.arccos((b**2+c**2-a**2)/(2*b*c)))
    elif output == "b":
        return np.degrees(np.arccos((c**2+a**2-b**2)/(2*c*a)))
    elif output == "c":
        return np.degrees(np.arccos((a**2+b**2-c**2)/(2*a*b)))
    
def fix_arm_point_pos(point, arm1Length, arm2Length):
    if point[2] < 0:
        point[2] = 0
    if point[0] == 0 and point[1] == 0 and point[2] == 0:
        return np.array([0, 0, arm1Length + arm2Length])
    point = move_outside_sphere(point, pythagoreanTheorem(arm1Length, arm2Length))
    point = move_inside_sphere(point, arm1Length + arm2Length)
    return point

# Do the Math
def arm(desiredPoint, arm1Length=250, arm2Length=250):
    """
    desiredPoint in x y z right forward up (from catbots's view)\n
    returns a tuple with (yaw, upperArm, lowerArm)
    """
    desiredPoint = np.array(desiredPoint)
    
    desiredPoint = fix_arm_point_pos(desiredPoint, arm1Length, arm2Length)
    desiredPoint = desiredPoint.astype(int)
    yaw = int(np.degrees(np.arctan2(desiredPoint[1], desiredPoint[0])))
    lengthXY = int(pythagoreanTheorem(desiredPoint[0], desiredPoint[1]))
    turretPitch = int(np.degrees(np.arctan2(desiredPoint[2], lengthXY)))
    lengthXYZ = int(vecLength(desiredPoint))
    angle_LengthXYZ_arm1Length = int(SSS(arm1Length, arm2Length, lengthXYZ,"b"))
    angle_arm1Length_arm2Length = int(SSS(arm1Length, arm2Length, lengthXYZ,"c") - 90)
    if yaw < 0:
        yaw += 180
        turretPitch = 180-turretPitch
        if turretPitch > 180:
            turretPitch -= 360
    angle_LengthXY_arm1Length = int(angle_LengthXYZ_arm1Length + turretPitch)
    
    # 0 = right, 0 = up, 90 = straight (order of print)
    return(yaw, angle_LengthXY_arm1Length, angle_arm1Length_arm2Length)

def pythagoreanTheorem(a, b, c=0):
    return np.sqrt(a**2+b**2+c**2)

def vecLength(vec):
    sum = 0
    for num in vec:
        sum += num**2
    return np.sqrt(sum)

def vecNormalize(vec):
    return vec / vecLength(vec)

def setVectorLength(vec, lenght):
    return vecNormalize(vec) * lenght
