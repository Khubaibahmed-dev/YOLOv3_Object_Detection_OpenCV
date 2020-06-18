import cv2
import argparse
import numpy as np

def load_input_image(image_path):
	
	test_img = cv2.imread(image_path)
	h, w, _ = test_img.shape

	return test_img, h, w


def yolov3(yolo_weights, yolo_cfg, coco_names):
	net = cv2.dnn.readNet(yolo_weights, yolo_cfg)
	classes = open(coco_names).read().strip().split("\n")
	layer_names = net.getLayerNames()
	output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

	return net, classes, output_layers


def perform_detection(net, img, output_layers):
	blob = cv2.dnn.blobFromImage(img, 1/255., (416,416), swapRB=True, crop=False)
	net.setInput(blob)
	layer_outputs = net.forward(output_layers)

	boxes = []
	confidences = []
	class_ids = []

	for output in layer_outputs:
	    for detection in output:
	        scores = detection[5:]
	        class_id = np.argmax(scores)
	        confidence = scores[class_id]

	        # Object is deemed to be detected
	        if confidence > confidence_threshold:
	            # center_x, center_y, width, height = (detection[0:4] * np.array([w, h, w, h])).astype('int')
	            center_x, center_y, width, height = list(map(int,detection[0:4] * [w, h, w, h]))
	            # print(center_x, center_y, width, height)

	            top_left_x = int(center_x - (width/2))
	            top_left_y = int(center_y - (height/2))

	            boxes.append([top_left_x, top_left_y, width, height])
	            confidences.append(float(confidence))
	            class_ids.append(class_id)


	return boxes, confidences, class_ids


def draw_boxes(boxes, confidences, class_ids, classes, img):
	colors = np.random.randint(0, 255, size=(len(classes), 3), dtype="uint8")

	indexes = cv2.dnn.NMSBoxes(boxes, confidence_threshold, NMS_threshold)

	FONT = cv2.FONT_HERSHEY_SIMPLEX

	if len(indexes) > 0:
    for i in indexes.flatten():
        x, y, w, h = boxes[i]
        # print(len(colors[class_ids[i]]))
        color = colors[i]
        cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
        text = f"{class_ids[i]} -- {confidences[i]}"
        text = "{}: {:.4f}".format(classes[class_ids[i]], confidences[i])
        cv2.putText(img, text, (x, y - 5), FONT, 0.5, color, 2)

    cv2.imshow("Detection", img)



if __name__ == '__main__':

	img, h, w = load_input_image("dining_table.jpg")
	net, classes, output_layers = yolov3("yolov3.weights", "yolov3.cfg", "coco.names")
	boxes, confidences, class_ids = perform_detection(net, img, output_layers)
	draw_boxes(boxes, confidences, class_ids, classes, img)