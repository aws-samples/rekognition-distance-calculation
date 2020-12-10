import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor
import math
import os


def calculateDistance(x1, y1, x2, y2):  
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
     return dist


def upload_image_to_s3(bucket_name, image_name):
    s3 = boto3.client('s3')

    bucket = bucket_name
    file_name = f"/tmp/{image_name}"

    object_key, extension = (image_name.split('.'))
    key_name = f"processed/{object_key}-processed.{extension}"

    s3.upload_file(file_name, bucket, key_name)


def detect_person_label(bucket_name, folder_name, object_name):

    # Carregando imagem do Bucket S3 para calcular o tamanho em pixels
    s3_connection = boto3.resource('s3')
    
    s3_object = s3_connection.Object(bucket_name, f"{folder_name}/{object_name}")
    s3_response = s3_object.get()

    # Lendo imagem utilizando PIL
    stream = io.BytesIO(s3_response['Body'].read())
    image = Image.open(stream)
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image) 

    # Largura e altura da imagem em Pixels
    print(f"Width: {imgWidth}, Height: {imgHeight}")

    # Utilizando Rekognition para pegar o BoundingBox
    client = boto3.client('rekognition')
    response = client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': f"{folder_name}/{object_name}",
            }
        }
    )
    get_preson = lambda item: item if item.get("Name") == "Person" else None
    person_list = list(filter(None, list(map(get_preson, response["Labels"]))))

    person_coordinate_list = []
    center_points = []

    # Realizando calculo do Boundingbox em relação ao tamanho da imagem em px
    for item in person_list[0]["Instances"]:
        # Calculando localização da caixa delimitadora em pixels
        box = item['BoundingBox']
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']

        # O primeiro ponto é sempre X o segundo é sempre Y (X, Y)
        points = (
            (left,top),
            (left + width, top),
            (left + width, top + height),
            (left , top + height),
            (left, top),
        )

        center = (left + (width/2), top + (height/2))
        draw.line(points, fill='#00d400', width=2)
        # draw.point(center, fill=255)
        draw.ellipse((center, (center[0] + 10, center[1] + 10)),fill='#00d400')
        center_points.append(center)

    # Ajustando a lista em ordem crescente
    sorted_center_list = sorted(center_points)

    count = 1
    for first_center in sorted_center_list:
        print(f"Person number {count}")
        count2 = 1
        for second_center in sorted_center_list:
            distance = calculateDistance(first_center[0], first_center[1], second_center[0], second_center[1])
            print(f"Distance from person {count} to person {count2} = {distance}px")
            count2 += 1

            # Distancia entre a pessoa para alertar via email utilizando SNS, apenas desenha a linah se for menor que 150 px
            if distance < int(os.getenv("PIXEL_DISTANCE", "150")):
                draw.line((first_center[0], first_center[1]-50, second_center[0], second_center[1]-50), fill='#fe0303', width=2)

                # Will save the image inside tmp folder to upload to s3 Bucket only if distance matches the conditional
                image.save(f"/tmp/{object_name}")
        count+=1
    
    

def lambda_handler(event, context):
    bucket = os.getenv("BUCKET_NAME", "rekognition-crowded")
    folder_name = os.getenv("S3_FOLDER_NAME", "to_process")

    # Object name will come from S3 event
    object_name = ((event["Records"][0]["s3"]["object"]["key"]).split("/"))[-1]

    detect_person_label(bucket, folder_name, object_name)

    # Upload imge to S3 after processing
    upload_image_to_s3(bucket, object_name)