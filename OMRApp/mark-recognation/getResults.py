import cv2
import numpy as np
import matplotlib.pyplot as plt
import json
import os


class Result:
    def __init__(self, path: str, number_of_questions: int = 45):
        self.path = path
        self.number_of_questions = number_of_questions
        self.image = cv2.imread(path, 0)
        
    def cropImage(self, img):
        """
        Crop the image into 4 parts.
        """
        # image resize (1280, 906)
        img = cv2.resize(img, (906, 1280))

        ##### changed
        img1 = img[515:515+394, 74:74+142]
        img2 = img[515:515+394, 239:239+142]
        img3 = img[515:515+394, 410:410+142]
        #####
    
        return img1, img2, img3
    
    def threshold(self, image):
        """
        Threshold the image.
        """
        # Blur
        image = cv2.GaussianBlur(image, (3, 3), 0)
        
        ret, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # erode the image
        kernel = np.ones((9, 9), np.uint8)
        thresh = cv2.erode(thresh, kernel, iterations = 1)

        return thresh
    
    def drawCircle(self, image, centers):
        """
        Draw the circle on the image.
        """
        # gray to RGB
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        for center in centers:
            cv2.circle(image, center, 5, (0, 0, 255), -1)
        return image

    def getAllResults(self, thresh_images, centers):
        # y_points = [25, 48, 70, 93, 117, 162, 186, 209, 232, 256, 302, 324, 348, 371, 395] changed to 
        y_points = [22, 43, 64, 87, 109, 152, 174, 196, 218, 240, 284, 305, 327, 350, 371]
        
        options = {1:"A", 2:"B", 3:"C", 4:"D"}
        # x_points = [18, 50, 78, 110] # x points +10 or -10 # changed to
        x_points = [34, 64, 94, 124] # x points +8 or -8
        # get results from thresh_images
        result = []
        for idx, y in enumerate(y_points, 1):
            answer = ""
            for i, x in enumerate(x_points, 1):
                r = thresh_images[y-8:y+8, x-8:x+8] ## changed
                
                b = 255 in r
                if b:
                    answer += options[i]
            result.append(answer)
            # replace "" to "empty"
            result = ["empty" if i == "" else i for i in result]
        return result


    def getContours(self, image):
        """
        Get the contours of the image.
        """
        contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def fixResult(self, points):
        points.sort(key=lambda x: x[1])
        i = 0
        while i < len(points):
            if i > 0:
                difference_y = points[i][1] - points[i-1][1]
                if difference_y < 10:
                    points[i-1] = (points[i-1], points.pop(i))

                if difference_y > 40 and i % 5 != 0:

                    p = (0, points[i-1][1] + 23)
                    points.insert(i, p)

            i += 1
        return points
    
    def getBoundingBoxCenter(self, contours):
        """
        Get the bounding box center of the contours.
        """
        boundingBoxes = [cv2.boundingRect(c) for c in contours]
        boundingBoxCenters = [(int(x + w/2), int(y + h/2)) for (x, y, w, h) in boundingBoxes]
        boundingBoxCenters = self.fixResult(boundingBoxCenters)

        return boundingBoxCenters
    
    def getOption(self, center):
        """
        Get the option of the center.
        """
        letters = {"A": 34, "B": 64, "C": 94, "D": 124} ## changed
        if center[0] > letters["A"] - 8 and center[0] < letters["A"] + 8:
            return "A"
        elif center[0] > letters["B"] - 8 and center[0] < letters["B"] + 8:
            return "B"
        elif center[0] > letters["C"] - 8 and center[0] < letters["C"] + 8:
            return "C"
        elif center[0] > letters["D"] - 8 and center[0] < letters["D"] + 8:
            return "D"
        else:
            return ""
        
    def getResults(self, centers):
        letters = {"A": 34, "B": 64, "C": 94, "D": 124} ## changed

        results = []
        for idx, center in enumerate(centers, 1):
            if type(center[0])  == tuple:
                answer = f"{self.getOption(center[0])},{self.getOption(center[1])}"
                results.append(answer)
            else:
                results.append(self.getOption(center))
        return results
    
    def result(self):
        """
        Get the result of the image.
        """
        crop_images = self.cropImage(self.image)
        thresh_images = [self.threshold(image) for image in crop_images]

        contours = [self.getContours(image) for image in thresh_images.copy()]
        centers = [self.getBoundingBoxCenter(contour) for contour in contours]

        results = [self.getAllResults(thresh, center) for thresh, center in zip(thresh_images, centers)]
        
        # add dictioanry
        all_results = []
        for result in results:
            all_results += result

        # to dict
        all_results = all_results[:self.number_of_questions]
        all_results = dict(zip(range(1, len(all_results) + 1), all_results))

        return all_results

class saveResults:

    def __init__(self, number_of_questions=50):
        self.number_of_questions = number_of_questions

    def inputFolder(self, folder):
        """
        Get the results from the folder.
        """
        # get all the files
        files = os.listdir(folder)
        # sort the files
        files = sorted(files, key=lambda x: int(x.split(".")[0][-2:]))
        # get the results
        results = {}
        for file in files:
            path = os.path.join(folder, file)
            
            result = Result(path, number_of_questions=self.number_of_questions)
            result = result.result()
            results[path] = result
        return results

    def saveResults(self, results : dict, output):
        """
        Save the results to json file.
        """
        r = list(dict())
        
        for key,value in results.items():
            r2 = list(dict())
            for key2,value2 in value.items():
                r2.append({"number":key2,"value":value2})
            r.append({"path":key, "result":r2})

        
        with open(output, "w") as f:
            json.dump(r, f, indent=4)

    


