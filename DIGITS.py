import cv2
import numpy as np
import math


cap = cv2.VideoCapture(0)
while(cap.isOpened()):
    # lire l'image
    ret, img = cap.read()
   
    # recevoir les donnees des mains a partir d'un rectangle 
    cv2.rectangle(img, (100,100), (300,300), (0,255,0),0)
    crop_img = img[100:300, 100:300]

    # transformer au grayscale
    grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    # appliquer gaussian blur
    value = (35, 35)
    blurred = cv2.GaussianBlur(grey, value, 0)

    # thresholdin: la methode d'Otsu's Binarization 
    _, thresh1 = cv2.threshold(blurred, 127, 255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    # afficher l'image thresholded 
    cv2.imshow('Thresholded', thresh1)

    #verifier la version d'OpenCV 
    (version, _, _) = cv2.__version__.split('.')

    if version == '3':
        image, contours, hierarchy = cv2.findContours(thresh1.copy(), \
               cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    elif version == '4':
        contours, hierarchy = cv2.findContours(thresh1.copy(),cv2.RETR_TREE, \
               cv2.CHAIN_APPROX_NONE)

    # trouver le contour avec max area
    cnt = max(contours, key = lambda x: cv2.contourArea(x))

    epsilon = 0.0005 * cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True)
    M = cv2.moments(cnt)
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    cv2.circle(crop_img, (cx, cy), 3, [0, 0, 0], -1)
    #utiliser le convex hull autour de la main
    hull = cv2.convexHull(cnt)

    #definir area du hull et area du hand
    areahull = cv2.contourArea(hull)
    areacnt = cv2.contourArea(cnt)

    #trouver le pourcentage d'area non couvré par la main en convex hull
    arearatio = ((areahull - areacnt) / areacnt) * 100

    #trouver les defects du convex hull en respectant la main
    hull = cv2.convexHull(approx, returnPoints=False)
    defects = cv2.convexityDefects(approx, hull)

    # l = no. de defects
    l = 0

    # code pour trouver no. of defects du aux doigts
    ptlist = []
    ptlist2 = []
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(approx[s][0])
        end = tuple(approx[e][0])
        far = tuple(approx[f][0])
        

        # trouver la longeur des cotes du triangles
        a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
        s = (a + b + c) / 2
        ar = math.sqrt(s * (s - a) * (s - b) * (s - c))

        #la distance entre le point et convex hull
        d = (2 * ar) / a

        # appliquer la regles de cosine
        angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

        # ignorer les angles > 90 et ignorer les points tres proches du convex hull
        if angle <= 90 and d > 30:
            l += 1
            cv2.circle(crop_img, far, 3, [255, 0, 0], -1)
            ptlist = ptlist + [start]
            ptlist2 = ptlist2 + [end]
        # dessiner des lignes autour de la main
        cv2.line(crop_img, start, end, [0, 255, 0], 2)

    l += 1
    

    font = cv2.FONT_HERSHEY_SIMPLEX

    rect = cv2.minAreaRect(cnt)
    _, _, ang = cv2.minAreaRect(cnt)

    myangle = str(ang)


    if l == 1:

            if arearatio < 11:
                cv2.putText(img, '10', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            elif arearatio <17 and  15< arearatio:
                cv2.putText(img, '0', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            else:
                cv2.putText(img, '1', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

    elif l == 2:
        cv2.putText(img, '2', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

    elif l == 3:
        ptlist = [ptlist[0], ptlist2[1]]
        distance = math.sqrt((ptlist[0][0] - ptlist[1][0]) ** 2 + (ptlist[1][1] - ptlist[0][1]) ** 2)
        distance2 = math.sqrt((ptlist[1][0] - cx) ** 2 + (ptlist[1][1] - cy) ** 2)
        slope = (ptlist[0][1] - cy) / (ptlist[0][0] - cx)
        slope2 = (ptlist[1][1] - cy) / (ptlist[1][0] - cx)
        angle = math.atan((slope - slope2) / (1 + (slope * slope2)))

        if -90 <= ang and ang <= -50:
            img = cv2.putText(img, "3", (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
        if -5 < ang and ang <= -0:
            if (abs(slope) > 2):
              img= cv2.putText(img, '6', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            else:
              img=  cv2.putText(img, '7', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            img = cv2.putText(img, str(abs(slope)), (150, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 2, cv2.LINE_AA)
        if -7 <= ang and ang <= -5:
            img = cv2.putText(img, "8", (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
        if -30 <= ang and ang <= -10:
            img = cv2.putText(img, "9", (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)

    elif l == 4:
        cv2.putText(img, '4', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

    elif l == 5:
        cv2.putText(img, '5', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

    else:
        cv2.putText(img, 'reposition', (10, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

    # Afficher la fenetre

    cv2.imshow('frame', img)


    k = cv2.waitKey(5) & 0xFF
    if k == ord('q'):
        break