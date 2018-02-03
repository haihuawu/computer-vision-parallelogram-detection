from PIL import Image
import math


matrixpoint = []
candidatepoint = []
candidateparalline = []
candidateimage = []
interpointarr = []
finalpointarr = []

#clear array
def cleararray():
    del matrixpoint[:]
    del candidatepoint[:]
    del candidateparalline[:]
    del candidateimage[:]
    del interpointarr[:]
    del finalpointarr[:]

#create gray image based on original image
def generate_gray_image(im,gray,width,height):
    for x in range(width):
        for y in range(height):
            r, g, b = im.getpixel((x,y))
            grayVal = (int)(0.3*r + 0.59*g + 0.11*b)
            gray.putpixel((x,y),grayVal)
    # gray.show()
    # gray.save('d:/lessons/S1-Image Vision/project/test3gray.jpg')

#sober operators,generate magnitude map
def generate_magnituide_map(imageName,gray,magImage,theta,width,height):
    for x in range(width):
        for y in range(height):
            if x == 0 or y == 0 or x == width-1 or y == height -1:
                magImage.putpixel((x,y),0)
            else:
                #caculate Gradient
                Gx = (gray.getpixel((x+1,y-1))+2*gray.getpixel((x+1,y))+gray.getpixel((x+1,y+1)) \
                - gray.getpixel((x-1,y-1)) - 2* gray.getpixel((x-1,y))-gray.getpixel((x-1,y+1)))/4
                Gy = (gray.getpixel((x-1,y-1))+ 2*gray.getpixel((x,y-1))+ gray.getpixel((x+1,y-1)) \
                - gray.getpixel((x-1,y+1)) - 2* gray.getpixel((x-1,y+1))- gray.getpixel((x+1,y+1)))/4

                mag = int(math.sqrt(Gx**2 + Gy**2) / math.sqrt(2))
                if imageName == "TestImage3.jpg":
                    mag = int(math.sqrt(Gx * Gx + Gy * Gy)) #/ math.sqrt(2))

                magImage.putpixel((x, y), mag)
                # print(x, y, Gx, Gy)
                if Gx != 0:
                    theta[y][x] = math.atan(Gy/Gx)*180.0/math.pi # [-90,90]
                    # print(int (theta[y][x]))
                else:
                    theta[y][x] = 90
    # magImage.show()  #the normalized gradient magnitude#################################
    #D:\lessons\S1-Image Vision\project
    # magImage.save('d:/lessons/S1-Image Vision/project/test3mag.jpg')

#quantize angle within 4 sectors
def quantize_angle(theta,width,height):
    for x in range(1,height-1):
        for y in range(1,width-1):
            if theta[x][y]>-22.5 and theta[x][y]<=22.5:
                theta[x][y] = 0
            elif theta[x][y]>22.5 and theta[x][y]<=67.5:
                theta[x][y] = 45
            elif theta[x][y]>-67.5 and theta[x][y]<=-22.5:
                theta[x][y] = -45;
            elif (theta[x][y]>=-90 and theta[x][y]<=-67.5) or (theta[x][y]>67.5 and theta[x][y]<=90):
                theta[x][y] = 90
            # print(theta[x][y])

#nonmaxima suppression to thin the edge
def nonmaxima_suppression(magImage,theta,width,height):
    for x in range(1,width-1):
        for y in range(1, height-1):
            if theta[y][x] == 0 and (magImage.getpixel((x,y))>magImage.getpixel((x-1,y)) and magImage.getpixel((x,y))>magImage.getpixel((x+1,y))):
                magImage.putpixel((x,y),0)
            elif theta[y][x] == 90 and (magImage.getpixel((x,y))>magImage.getpixel((x,y-1)) and magImage.getpixel((x,y))>magImage.getpixel((x,y+1))):
                magImage.putpixel((x, y), 0)
            elif theta[y][x] == 45 and (magImage.getpixel((x,y))>magImage.getpixel((x+1,y-1)) and magImage.getpixel((x,y))>magImage.getpixel((x-1,y+1))):
                magImage.putpixel((x, y), 0)
            elif theta[y][x] == -45 and (magImage.getpixel((x,y))>magImage.getpixel((x-1,y-1)) and magImage.getpixel((x,y))>magImage.getpixel((x+1,y+1))):
                magImage.putpixel((x, y), 0)

#generate binary edge map by magnitude threshold
def generate_binary_edge_map(magImage,width,height,magThreshold):
    print("magThreshold is ",str(magThreshold))
    for x in range(width):
        for y in range(height):
            #bg 255,fg 0
            mag = magImage.getpixel((x,y))
            if mag > magThreshold:
                magImage.putpixel((x, y), 0)
                # print(x, y)
            else:
                magImage.putpixel((x, y), 255)

    # magImage.show() # the edge map after thresholding##############################
    # magImage.save('d:/lessons/S1-Image Vision/project/test3edge.jpg')

#hough transform [0,180] p: -1008，1008 pmax is (w+h)*2
# quantize the parameter space and initialize all cells to zero
def generate_p_theta_matrix(magImage,Matrix,width,height,tangleMax):
    for x in range(width):
        for y in range(height):
            if magImage.getpixel((x,y)) == 0:
                for tangle in range(tangleMax):
                    P = int(x * math.cos(tangle * math.pi / 180.0) + y * math.sin(tangle * math.pi / 180.0))
                    if tangleMax == 37:
                        P = int(x * math.cos(tangle * 5 * math.pi / 180.0) + y * math.sin(tangle * 5 * math.pi / 180.0))
                        # print(x,y,tangle,P,P+width)
                    matrixI = P+width+height
                    matrixJ = tangle
                    # accumulators
                    # print(matrixI,matrixJ)

                    Matrix[matrixI][matrixJ] += 1

#initialize result image
def initialize_result_img(resultImg,width,height):
    for x in range(width):
        for y in range(height):
            resultImg.putpixel((x,y),255)

#check if the point is in an edge
def is_edge(x,y,width,height,magImage,resultImg):
    bflag = False
    if magImage.getpixel((x, y)) == 0 \
            or (y - 1 > -1 and resultImg.getpixel((x, y - 1)) == 0) \
            or (y + 1 < height and resultImg.getpixel((x, y + 1)) == 0) \
            or (x - 1 > -1 and resultImg.getpixel((x - 1, y)) == 0) \
            or (x + 1 < width and resultImg.getpixel((x + 1, y)) == 0) \
            or (x - 1 > -1 and y - 1 > -1 and resultImg.getpixel((x - 1, y - 1)) == 0) \
            or (x + 1 < width and y + 1 < height and resultImg.getpixel((x + 1, y + 1)) == 0) \
            or (x - 1 > -1 and y + 1 < height and resultImg.getpixel((x - 1, y + 1)) == 0) \
            or (x + 1 < width and y - 1 > -1 and resultImg.getpixel((x + 1, y - 1)) == 0):
            # or (x - 2 > -1 and y - 2 > -1 and resultImg.getpixel((x - 2, y - 2)) == 0) \
            # or (x - 1 > -1 and y - 2 > -1 and resultImg.getpixel((x - 1, y - 2)) == 0) \
            # or (y - 2 > -1 and resultImg.getpixel((x, y - 2)) == 0) \
            # or (x + 1 < width and y - 2 > -1 and resultImg.getpixel((x + 1, y - 2)) == 0) \
            # or (x + 2 < width and y - 2 > -1 and resultImg.getpixel((x + 2, y - 2)) == 0) \
            # or (x + 2 < width and y - 1 > -1 and resultImg.getpixel((x + 2, y - 1)) == 0) \
            # or (x + 2 < width and resultImg.getpixel((x + 2, y)) == 0) \
            # or (x + 2 < width and y + 1 < height and resultImg.getpixel((x + 2, y + 1)) == 0) \
            # or (x + 2 < width and y + 2 < height and resultImg.getpixel((x + 2, y + 2)) == 0) \
            # or (x + 1 < width and y + 2 < height and resultImg.getpixel((x + 1, y + 2)) == 0) \
            # or (y + 2 < height and resultImg.getpixel((x, y + 2)) == 0) \
            # or (x - 1 > -1 and y + 2 < height and resultImg.getpixel((x - 1, y + 2)) == 0) \
            # or (x - 2 > -1 and y + 2 < height and resultImg.getpixel((x - 2, y + 2)) == 0) \
            # or (x - 2 > -1 and y - 1 > -1 and resultImg.getpixel((x - 2, y - 1)) == 0) \
            # or (x - 2 > -1 and resultImg.getpixel((x - 2, y)) == 0) \
            # or (x - 2 > -1 and y - 1 > -1 and resultImg.getpixel((x - 2, y - 1)) == 0):
        bflag = True
    return bflag

#save p theta its accumulator value is larger than threshold in an array
def generate_p_theta_array(Matrix,pMax,accThreshold,tangleMax):
    index = 0
    print("pMax,tangleMax,accThreshold is "+ str(pMax)+" "+str(tangleMax)+" "+str(accThreshold))
    for x in range(pMax):
        for y in range(tangleMax):
            if Matrix[x][y] > accThreshold:
                # print(x,y,Matrix[x][y])
                matrixpoint.append([x,y,Matrix[x][y]])# p,theta,a
                # print(matrixpoint[index])
                index += 1
    print("==========p_theta_array==========")
    for x in range(len(matrixpoint)):
        print(matrixpoint[x])
    print("==========p_theta_array==========")
    return index

#sort function
def takeSecond(elem):
    return elem[1]

#remove some point in p-theta array
def generate_p_theta_candidate_array(gaptheta,gapp,imageName):
    cpindex = 1
    candidatepoint.append([matrixpoint[0][0], matrixpoint[0][1],matrixpoint[0][2]])
    # print(candidatepoint[0][0], candidatepoint[0][1],matrixpoint[0][2])
    index = len(matrixpoint)
    for i in range(1, index):
        flag = True
        if imageName == "TestImage1c.jpg":
            for j in range(cpindex):
                if abs(matrixpoint[i][1] - candidatepoint[j][1]) < gaptheta \
                        and abs(matrixpoint[i][0] - candidatepoint[j][0]) < gapp:
                    flag = False
                    break
            if flag == True:
                candidatepoint.append(matrixpoint[i])
                cpindex += 1
        else:
            tempindex = -1
            for j in range(cpindex):
                if abs(matrixpoint[i][1] - candidatepoint[j][1]) < gaptheta and abs(
                                matrixpoint[i][0] - candidatepoint[j][0]) < gapp:  # <2
                    flag = False
                    if matrixpoint[i][2] > candidatepoint[j][2]:
                        tempindex = j
                    break
            if tempindex != -1:
                candidatepoint[tempindex] = matrixpoint[i]

            if flag == True:
                candidatepoint.append([matrixpoint[i][0], matrixpoint[i][1], matrixpoint[i][2]])
                # print(candidatepoint[cpindex][0], candidatepoint[cpindex][1],candidatepoint[cpindex][2])
                cpindex += 1

    candidatepoint.sort(key = takeSecond)
    print("++++++++++Candidate+++++++++++")
    for i in range(len(candidatepoint)):
        print(candidatepoint[i])
    print("++++++++++Candidate+++++++++++")
    return cpindex

#generate image after hough transform
def generate_image_after_hough_transform(magImage,resultImg,cpindex,width,height,tangleMax):
    for c in range(cpindex):
        for i in range(width):
            for j in range(height):
                if(magImage.getpixel((i,j)) == 0):
                    thetamag = candidatepoint[c][1]*math.pi/180.0
                    if tangleMax == 37:
                        thetamag = candidatepoint[c][1] * 5 * math.pi / 180.0
                    tempP = int (i*math.cos(thetamag)+j*math.sin(thetamag)) + width + height
                    #print(tempP,x)
                    if(int(tempP) == int (candidatepoint[c][0])):
                        resultImg.putpixel((i,j),0)
                        # print(i,j)
    # resultImg.show()

#generate candidate parallel line
def generate_candidate_line(resultImg,width,height,cpindex,imageName):
    initialize_result_img(resultImg, width, height)
    if imageName == "TestImage1c.jpg":
        for i in range(cpindex):
            for j in range(i+1,cpindex):
                if candidatepoint[j][1] - candidatepoint[i][1] < 6:
                    candidateparalline.append(
                        [candidatepoint[i][0], candidatepoint[i][1], candidatepoint[j][0], candidatepoint[j][1]])
    elif imageName == "TestImage2c.jpg":
        if width > 500:
            for i in range(cpindex):
                for j in range(i + 1, cpindex):
                    if candidatepoint[j][1] - candidatepoint[i][1] < 3 \
                            and abs(candidatepoint[j][0] - candidatepoint[i][0]) > 50:
                        candidateparalline.append(
                            [candidatepoint[i][0], candidatepoint[i][1], candidatepoint[j][0], candidatepoint[j][1]])
                        # print("===========1=============")
                        # print(candidatepoint[i][0],candidatepoint[i][1],candidatepoint[j][0],candidatepoint[j][1])
                    elif candidatepoint[j][1] > 33:
                        temptheta = abs(candidatepoint[j][1] - 36)
                        if abs(temptheta - candidatepoint[i][1]) < 3 and abs(
                                        candidatepoint[j][0] - candidatepoint[i][0]) > 50:
                            candidateparalline.append(
                                [candidatepoint[i][0], candidatepoint[i][1], candidatepoint[j][0], candidatepoint[j][1]])
        else:
            for i in range(cpindex):
                for j in range(i + 1, cpindex):
                    if candidatepoint[j][1] - candidatepoint[i][1] < 14 \
                            and abs(candidatepoint[j][0] - candidatepoint[i][0]) > 52:
                        candidateparalline.append(
                            [candidatepoint[i][0], candidatepoint[i][1], candidatepoint[j][0], candidatepoint[j][1]])
                    elif candidatepoint[j][1] == 180:
                        if candidatepoint[i][1] < 14 and abs(candidatepoint[j][0] - candidatepoint[i][0]) > 52:
                            candidateparalline.append(
                                [candidatepoint[i][0], candidatepoint[i][1], candidatepoint[j][0], candidatepoint[j][1]])

    else:
        for i in range(cpindex):
            if candidatepoint[i][1] < 88 and candidatepoint[i][1] > 7:
                continue
            for j in range(i+1,cpindex):
                if candidatepoint[j][1] < 88 and candidatepoint[j][1] > 7:
                    continue
                if candidatepoint[i][1]!= 0 and candidatepoint[j][1] - candidatepoint[i][1] < 7 \
                    and abs(candidatepoint[j][0]-candidatepoint[i][0]) > 100:
                    candidateparalline.append([candidatepoint[i][0],candidatepoint[i][1],candidatepoint[j][0],candidatepoint[j][1]])

                    #test////////////////////////////////////////////////////////
    print("=======candidate line===========")
    for c in range(len(candidateparalline)):
        print(candidateparalline[c])
        for i in range(width):
            for j in range(height):
                # if(magImage.getpixel((i,j)) == 0):
                    thetamag = candidateparalline[c][1]*math.pi/180.0
                    tempP = int (i*math.cos(thetamag)+j*math.sin(thetamag)) + width + height
                    #print(tempP,x)
                    if(int(tempP) == int (candidateparalline[c][0])):
                        resultImg.putpixel((i,j),0)
                    thetamag = candidateparalline[c][3] * math.pi / 180.0
                    tempP = int(i * math.cos(thetamag) + j * math.sin(thetamag)) + width + height
                    # print(tempP,x)
                    if (int(tempP) == int(candidateparalline[c][2])):
                        resultImg.putpixel((i, j), 0)
    print("=======candidate line===========")
    # resultImg.show()
    return len(candidateparalline)

#generate candidate parallel image
def generate_candidate_image(linecount,imageName,type):
    for i in range(linecount):
        for j in range(i+1,linecount):
            tempthetai1 = candidateparalline[i][1]
            tempthetai2 = candidateparalline[i][3]
            tempthetaj1 = candidateparalline[j][1]
            tempthetaj2 = candidateparalline[j][3]
            if imageName == "TestImage2c.jpg":
                if type == 1:
                    if tempthetai1 > 18:
                        tempthetai1 = abs(tempthetai1 - 36)
                    if tempthetai2 > 18:
                        tempthetai2 = abs(tempthetai2 - 36)
                    if tempthetaj1 > 18:
                        tempthetaj1 = abs(tempthetaj1 - 36)
                    if tempthetaj2 > 18:
                        tempthetaj2 = abs(tempthetaj2 - 36)
                    if candidateparalline[i][0] != candidateparalline[j][0] \
                            and candidateparalline[i][0] != candidateparalline[j][2] \
                            and candidateparalline[i][2] != candidateparalline[j][0] \
                            and candidateparalline[i][2] != candidateparalline[j][2] \
                            and abs(tempthetai1 - tempthetaj1) > 9 \
                            and abs(tempthetai1 - tempthetaj2) > 9 \
                            and abs(tempthetai2 - tempthetaj1) > 9 \
                            and abs(tempthetai2 - tempthetaj2) > 9:
                        candidateimage.append([i, j])
                else:
                    if abs(tempthetai1 - tempthetaj1) > 38 \
                            and abs(tempthetai1 - tempthetaj2) > 38 \
                            and abs(tempthetai2 - tempthetaj1) > 38 \
                            and abs(tempthetai2 - tempthetaj2) > 38:
                        candidateimage.append([i, j])
            else:
                if abs(tempthetai1-tempthetaj1) > 10 \
                    and abs(tempthetai1 - tempthetaj2) > 10 \
                    and abs(tempthetai2 - tempthetaj1) > 10 \
                    and abs(tempthetai2 - tempthetaj2) > 10:
                        candidateimage.append([i,j])
    print("++++++++candidate image+++++++")
    for i in range(len(candidateimage)):
         print(candidateimage[i])
    print("++++++++candidate image+++++++")
    return len(candidateimage)

#compute interpointer of those parallel image
def compute_interpoint(p1,theta1,p2,theta2,width,height,tangleMax):
    print(p1,theta1,p2,theta2)
    newtheta1 = theta1 * math.pi / 180.0
    newtheta2 = theta2 * math.pi / 180.0
    if tangleMax == 37:
        newtheta1 = theta1 * 5 * math.pi / 180.0
        newtheta2 = theta2 * 5 * math.pi / 180.0

    newp1 = p1 - width - height
    newp2 = p2 - width - height
    x = int((math.sin(newtheta1) * newp2 - math.sin(newtheta2) * newp1) / (
        math.sin(newtheta1) * math.cos(newtheta2) - math.sin(newtheta2) * math.cos(newtheta1)))

    if theta1 == 0:
        y = int((newp2 - ((math.sin(newtheta1) * newp2 - math.sin(newtheta2) * newp1) / (
        math.sin(newtheta1) * math.cos(newtheta2) - math.sin(newtheta2) * math.cos(newtheta1))) * math.cos(newtheta2)) / math.sin(newtheta2))
    else:
        y = int((newp1 - ((math.sin(newtheta1) * newp2 - math.sin(newtheta2) * newp1) / (
        math.sin(newtheta1) * math.cos(newtheta2) - math.sin(newtheta2) * math.cos(newtheta1))) * math.cos(newtheta1)) / math.sin(newtheta1))

    # print(x,y)
    interpointarr.append([x,y])

#filter some interpoint if the point if out of range
def filter_interpoint(im,width,height):
    print("+++++++++++++inter point++++++++++")
    for i in range(0,len(interpointarr)):
        print(interpointarr[i])
    print("+++++++++++++inter point++++++++++")
    for i in range(0,len(interpointarr),4):
        flag = True
        for j in range(i,i+4):
            if interpointarr[j][0] < 0 or interpointarr[j][1] < 0 \
                or interpointarr[j][0] >= width or interpointarr[j][1] >= height:
                flag = False
                break
        for p in range(i,i+3):
            for q in range(p+1,i+4):
                if interpointarr[p][0] == interpointarr[q][0]\
                        and interpointarr[p][1] == interpointarr[q][1]:
                    flag = False
                break

        if flag == True:
            x1 = interpointarr[i][0]
            y1 = interpointarr[i][1]
            x2 = interpointarr[i+1][0]
            y2 = interpointarr[i+1][1]
            x3 = interpointarr[i+2][0]
            y3 = interpointarr[i+2][1]
            x4 = interpointarr[i+3][0]
            y4 = interpointarr[i+3][1]
            finalpointarr.append([x1,y1,x2,y2,x3,y3,x4,y4]) #x1,y1,x2,y2,x3,y3,x4,y4
            print(x1,y1,x2,y2,x3,y3,x4,y4)
            im.putpixel((x1, y1), (255, 0, 0))
            im.putpixel((x2, y2), (255, 0, 0))
            im.putpixel((x3, y3), (255, 0, 0))
            im.putpixel((x4, y4), (255, 0, 0))

#get edge point number
def get_edge_point_count(x1,y1,x2,y2):
    if x1 == x2:  # vertical
        min = y1
        max = y2
        if y1 > y2:
            min = y2
            max = y1
        edgepoint = 0
        for y in range(min, max + 1):
            bflag = is_edge(x1, y)
            if bflag == True:
                edgepoint += 1
    elif abs(x1-x2) < abs(y1-y2):
        m = (y1 - y2) / (x1 - x2)
        c = y1 - x1 * m
        min = y1
        max = y2
        if y1 > y2:
            min = y2
            max = y1
        edgepoint = 0
        for y in range(min, max + 1):
            x = int((y-c)/m)
            bflag = is_edge(x, y)
            if bflag == True:
                edgepoint += 1
    else:
        m = (y1 - y2) / (x1 - x2)
        c = y1 - x1 * m
        min = x1
        max = x2
        if x2 < x1:
            min = x2
            max = x1
        edgepoint = 0
        for x in range(min, max+1):
            y = int(m * x + c)
            bflag = is_edge(x, y)
            if bflag == True:
                edgepoint += 1
    return edgepoint

#plot the line
def plot_line(im,x1,y1,x2,y2,impre,type):
    if x1 == x2:  # vertical
        min = y1
        max = y2
        if y1 > y2:
            min = y2
            max = y1
        for y in range(min, max + 1):
            im.putpixel((x1, y), (255, 0, 0))
            if impre != None:
                if type == 2:
                    impre.putpixel((x1 + 560, y), (255, 0, 0))
                else:
                    impre.putpixel((x1, y), (255, 0, 0))
    elif abs(x1-x2) < abs(y1-y2):
        m = (y1 - y2) / (x1 - x2)
        c = y1 - x1 * m
        min = y1
        max = y2
        if y1 > y2:
            min = y2
            max = y1
        for y in range(min, max + 1):
            x = int ((y-c)/m)
            im.putpixel((x, y), (255, 0, 0))
            if impre != None:
                if type == 2:
                    impre.putpixel((x + 560, y), (255, 0, 0))
                else:
                    impre.putpixel((x, y), (255, 0, 0))
    else:
        m = (y1 - y2) / (x1 - x2)
        c = y1 - x1 * m
        min = x1
        max = x2
        if x2 < x1:
            min = x2
            max = x1
        for x in range(min, max+1):
            y = int(m * x + c)
            im.putpixel((x,y),(255,0,0))
            if impre != None:
                if type == 2:
                    impre.putpixel((x + 560, y), (255, 0, 0))
                else:
                    impre.putpixel((x, y), (255, 0, 0))

#find interpoint
def find_interpoint(imgcount,width,height,tangleMax):
    for i in range(imgcount):
        # 1
        theta1 = candidateparalline[candidateimage[i][0]][1]
        p1 = candidateparalline[candidateimage[i][0]][0]
        # 2
        theta2 = candidateparalline[candidateimage[i][0]][3]
        p2 = candidateparalline[candidateimage[i][0]][2]
        # 7
        theta3 = candidateparalline[candidateimage[i][1]][1]
        p3 = candidateparalline[candidateimage[i][1]][0]
        # 8
        theta4 = candidateparalline[candidateimage[i][1]][3]
        p4 = candidateparalline[candidateimage[i][1]][2]

        compute_interpoint(p1,theta1,p3,theta3,width,height,tangleMax)
        compute_interpoint(p1,theta1,p4,theta4,width,height,tangleMax)
        compute_interpoint(p2,theta2,p3,theta3,width,height,tangleMax)
        compute_interpoint(p2,theta2,p4,theta4,width,height,tangleMax)

#compute distance between two points
def distance(x1,y1,x2,y2):
    dist = int(math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))
    return dist

#do edge segment detection
def edge_segment_detection(impre,im,magImage,resultImg,Matrix,pMax,width,height,gaptheta,gapp,perT,accThreshold,imageName,tangleMax,type):
    index = generate_p_theta_array(Matrix,pMax,accThreshold,tangleMax)
    print(index)

    cpindex = generate_p_theta_candidate_array(gaptheta,gapp,imageName)
    print(cpindex)

    generate_image_after_hough_transform(magImage,resultImg,cpindex,width,height,tangleMax)

    linecount = generate_candidate_line(resultImg,width,height,cpindex,imageName)
    print(linecount)

    imgcount = generate_candidate_image(linecount,imageName,type)
    print(imgcount)
    #
    #find interpoint
    find_interpoint(imgcount,width,height,tangleMax)
    #
    filter_interpoint(im,width,height)
    for i in range(len(finalpointarr)):
        dist1 = distance(finalpointarr[i][0],finalpointarr[i][1],finalpointarr[i][2],finalpointarr[i][3])
        dist2 = distance(finalpointarr[i][0], finalpointarr[i][1], finalpointarr[i][4], finalpointarr[i][5])
        dist3 = distance(finalpointarr[i][2], finalpointarr[i][3], finalpointarr[i][6], finalpointarr[i][7])
        dist4 = distance(finalpointarr[i][4], finalpointarr[i][5], finalpointarr[i][6], finalpointarr[i][7])

        # totalpoint = totalpoint1+totalpoint2+totalpoint3+totalpoint4

        edgepoint = 0
        totalpoint = 0
        maxX = max(finalpointarr[i][0],finalpointarr[i][2])
        minX = min(finalpointarr[i][0],finalpointarr[i][2])
        maxY = max(finalpointarr[i][1], finalpointarr[i][3])
        minY = min(finalpointarr[i][1], finalpointarr[i][3])
        pointTheta = math.pi / 2
        if finalpointarr[i][3] != finalpointarr[i][1]:
            pointTheta = math.atan((finalpointarr[i][0] - finalpointarr[i][2]) / (finalpointarr[i][3] - finalpointarr[i][1]))
        pointP = int (finalpointarr[i][0]*math.cos(pointTheta)+finalpointarr[i][1]*math.sin(pointTheta))

        for x in range(minX,maxX):
            for y in range(minY,maxY):
                AC = distance(x,y,finalpointarr[i][0],finalpointarr[i][1])
                BC = distance(x,y,finalpointarr[i][2],finalpointarr[i][3])
                tempP = int (x*math.cos(pointTheta)+y*math.sin(pointTheta))
                if AC+BC == dist1 and tempP == pointP:
                    totalpoint += 1
                    if magImage.getpixel((x, y)) == 0:
                        edgepoint+=1

        maxX = max(finalpointarr[i][0], finalpointarr[i][4])
        minX = min(finalpointarr[i][0], finalpointarr[i][4])
        maxY = max(finalpointarr[i][1], finalpointarr[i][5])
        minY = min(finalpointarr[i][1], finalpointarr[i][5])
        pointTheta = math.pi / 2
        if finalpointarr[i][5] != finalpointarr[i][1]:
            pointTheta = math.atan((finalpointarr[i][0] - finalpointarr[i][4]) / (finalpointarr[i][5] - finalpointarr[i][1]))
        pointP = int(finalpointarr[i][0] * math.cos(pointTheta) + finalpointarr[i][1] * math.sin(pointTheta))

        for x in range(minX,maxX):
            for y in range(minY,maxY):
                AC = distance(x, y, finalpointarr[i][0], finalpointarr[i][1])
                BC = distance(x, y, finalpointarr[i][4], finalpointarr[i][5])
                tempP = int(x * math.cos(pointTheta) + y * math.sin(pointTheta))
                if AC+BC == dist2 and tempP == pointP:
                    totalpoint += 1
                    if magImage.getpixel((x, y)) == 0:
                        edgepoint += 1

        maxX = max(finalpointarr[i][2], finalpointarr[i][6])
        minX = min(finalpointarr[i][2], finalpointarr[i][6])
        maxY = max(finalpointarr[i][3], finalpointarr[i][7])
        minY = min(finalpointarr[i][3], finalpointarr[i][7])
        pointTheta = math.pi / 2
        if finalpointarr[i][7] != finalpointarr[i][3]:
            pointTheta = math.atan(
                (finalpointarr[i][2] - finalpointarr[i][6]) / (finalpointarr[i][7] - finalpointarr[i][3]))
        pointP = int(finalpointarr[i][2] * math.cos(pointTheta) + finalpointarr[i][3] * math.sin(pointTheta))

        for x in range(minX, maxX):
            for y in range(minY, maxY):
                AC = distance(x, y, finalpointarr[i][2], finalpointarr[i][3])
                BC = distance(x, y, finalpointarr[i][6], finalpointarr[i][7])
                tempP = int(x * math.cos(pointTheta) + y * math.sin(pointTheta))
                if AC + BC == dist3 and tempP == pointP:
                    totalpoint += 1
                    if magImage.getpixel((x, y)) == 0:
                        edgepoint += 1

        maxX = max(finalpointarr[i][4], finalpointarr[i][6])
        minX = min(finalpointarr[i][4], finalpointarr[i][6])
        maxY = max(finalpointarr[i][5], finalpointarr[i][7])
        minY = min(finalpointarr[i][5], finalpointarr[i][7])
        pointTheta = math.pi / 2
        if finalpointarr[i][5] != finalpointarr[i][7]:
            pointTheta = math.atan(
                (finalpointarr[i][4] - finalpointarr[i][6]) / (finalpointarr[i][7] - finalpointarr[i][5]))
        pointP = int(finalpointarr[i][4] * math.cos(pointTheta) + finalpointarr[i][5] * math.sin(pointTheta))

        for x in range(minX, maxX):
            for y in range(minY, maxY):
                AC = distance(x, y, finalpointarr[i][4], finalpointarr[i][5])
                BC = distance(x, y, finalpointarr[i][6], finalpointarr[i][7])
                tempP = int(x * math.cos(pointTheta) + y * math.sin(pointTheta))
                if AC + BC == dist4 and tempP == pointP:
                    totalpoint += 1
                    if magImage.getpixel((x, y)) == 0:
                        edgepoint += 1

        print("edgepoint,totalpoint")
        print(edgepoint,totalpoint)
        if edgepoint/totalpoint>perT:
            plot_line(im,finalpointarr[i][0], finalpointarr[i][1], finalpointarr[i][2], finalpointarr[i][3],impre,type)
            plot_line(im,finalpointarr[i][0], finalpointarr[i][1], finalpointarr[i][4], finalpointarr[i][5],impre,type)
            plot_line(im,finalpointarr[i][2], finalpointarr[i][3], finalpointarr[i][6], finalpointarr[i][7],impre,type)
            plot_line(im,finalpointarr[i][4], finalpointarr[i][5], finalpointarr[i][6], finalpointarr[i][7],impre,type)

#joint two images
def image_joint(img1,img2):
    new_img = Image.new('L', (1008, 756))
    new_img.paste(img1,(0,0))
    new_img.paste(img2,(560,0))
    # new_img.show()
    # new_img.save('d:/lessons/S1-Image Vision/project/test2gray.jpg')

#detect parallel image for image 1 and 3
def detectparallel(imageName,magThreshold,accThreshold,gaptheta,gapp,perT,tangleMax):
    #clear array
    cleararray()
    #read image
    im = Image.open(imageName)
    width, height = im.size
    print(width,height,im.mode)
    pMax = (width+height)*2
    #show orginal image
    #im.show()
    # show gray scale image , convert rgb to grayscale
    gray = Image.new('L', (width, height))
    generate_gray_image(im,gray,width,height)
    #gray.show()

    magImage = Image.new('L',(width, height))
    #theta magnitude angle
    theta = [[0 for x in range(width)] for y in range(height)]
    generate_magnituide_map(imageName,gray,magImage,theta,width,height)
    if imageName != "TestImage3.jpg":
        quantize_angle(theta,width,height)
        nonmaxima_suppression(magImage,theta,width,height)
    generate_binary_edge_map(magImage,width,height,magThreshold)

    Matrix = [[0 for x in range(tangleMax)] for y in range(pMax)]
    generate_p_theta_matrix(magImage,Matrix,width,height,tangleMax)

    #initialize result image
    resultImg = Image.new('L', (width, height))
    initialize_result_img(resultImg,width,height)




    edge_segment_detection(None,im,magImage, resultImg, Matrix,pMax,width, height,\
                           gaptheta,gapp,perT,accThreshold,imageName,tangleMax,0)

    # # resultImg.show()
    # # resultImg.save('d:/lessons/S1-Image Vision/project/test1interline.jpg')
    #
    im.show()
    # im.save('d:/lessons/S1-Image Vision/project/test1result.jpg')

#detect paral1el image for image 2
def detectparallel2(imageName,magThreshold1,tangleMax1,magThreshold2,tangleMax2):
    # clear array
    cleararray()
    impre = Image.open(imageName)
    im1 = impre.crop((0, 0, 570, 756))
    im2 = impre.crop((560, 0, 1008, 756))
    # im1.show()

    width, height = im1.size
    print(width, height, im1.mode)

    pMax = (width + height) * 2
    # show orginal image
    # im.show()
    gray = Image.new('L', (width, height))

    generate_gray_image(im1, gray,width,height)
    image_list = []
    image_list.append(gray)
    # show gray image , convert rgb to grayscale
    # gray.show()

    magImage = Image.new('L',(width, height))

    #theta magnitude angle
    theta = [[0 for x in range(width)] for y in range(height)]

    generate_magnituide_map(imageName,gray,magImage,theta,width,height)

    tempmagImg = Image.new('L',(width, height))
    tempmagImg.paste(magImage,(0,0))
    image_list.append(tempmagImg)

    quantize_angle(theta,width,height)
    nonmaxima_suppression(magImage,theta,width,height)
    generate_binary_edge_map(magImage,width,height,magThreshold1)
    # image_list.append(magImage)
    Matrix = [[0 for x in range(tangleMax1)] for y in range(pMax)]
    generate_p_theta_matrix(magImage,Matrix,width,height,tangleMax1)

    #initialize result image
    resultImg = Image.new('L', (width, height))
    initialize_result_img(resultImg,width,height)
    edge_segment_detection(impre,im1, magImage, resultImg, Matrix, pMax, width, height, 8, 50, 0.15, 33,imageName, tangleMax1,1)


    # resultImg.show()
    # resultImg.save('d:/lessons/S1-Image Vision/project/test1interline.jpg')

    # im1.show()
    # im.save('d:/lessons/S1-Image Vision/project/test1result.jpg')
    # impre.show()

    cleararray()

    width, height = im2.size
    print(width, height, im2.mode)
    pMax = (width + height) * 2
    gray2 = Image.new('L', (width, height))

    print(width, height)
    generate_gray_image(im2, gray2,width,height)
    image_list.append(gray2)
    # show gray image , convert rgb to grayscale
    # gray2.show()
    magImage2 = Image.new('L',(width, height))
    theta2 = [[0 for x in range(width)] for y in range(height)]
    generate_magnituide_map(imageName,gray2,magImage2,theta2,width,height)

    tempmagImg2 = Image.new('L', (width, height))
    tempmagImg2.paste(magImage2, (0, 0))
    image_list.append(tempmagImg2)

    # quantize_angle(theta2, width, height)
    # nonmaxima_suppression(magImage2, theta2, width, height)
    generate_binary_edge_map(magImage2,width,height,magThreshold2)
    # image_list.append(magImage2)

    Matrix2 = [[0 for x in range(tangleMax2)] for y in range(pMax)]
    generate_p_theta_matrix(magImage2,Matrix2,width,height,tangleMax2)

    resultImg2 = Image.new('L', (width, height))
    initialize_result_img(resultImg2,width,height)
    edge_segment_detection(impre,im2,magImage2,resultImg2,Matrix2,pMax,width,height,10,52,0.15,53,imageName,tangleMax2,2)
    # edge_segment_detection(impre, im, magImage, resultImg, Matrix, pMax, width, height, gaptheta, gapp, perT,
    #                        accThreshold, imageName, tangleMax, type):

    # resultImg2.show()
    # im2.show()
    # im.save('d:/lessons/S1-Image Vision/project/test1result.jpg')
    impre.show()
    # impre.save('d:/lessons/S1-Image Vision/project/test2result.jpg')


    image_joint(image_list[0],image_list[2])
    image_joint(image_list[1],image_list[3])
    # image_joint(image_list[2],image_list[5])


#main function to call detect parallel images
detectparallel2("TestImage2c.jpg",32,37,100,181)
# detectparallel2(imageName,magThreshold1,tangleMax1,magThreshold2,tangleMax2):
# image 3 magnitude threshold : 28, accumulator threshold : 50
detectparallel("TestImage1c.jpg",32,67,2,50,0.14,181)
detectparallel("TestImage3.jpg",28,50,15,30,0.4,180)
#detectparallel(imageName,magThreshold,accThreshold,gaptheta,gapp,perT,tangleMax)
#

