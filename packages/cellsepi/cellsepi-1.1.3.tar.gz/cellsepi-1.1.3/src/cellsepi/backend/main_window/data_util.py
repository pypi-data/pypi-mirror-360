import base64
import os
import pathlib
import platform
import shutil
import stat
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import numpy as np
from PIL import Image
from bioio import BioImage
import bioio_lif


def listdir(directory):
    dir_list = [directory / elem for elem in os.listdir(directory)]
    return dir_list


def organize_files(files, channel_prefix, mask_suffix=""):
    id_to_file = {}
    for file in files:
        if channel_prefix in file.name:
            image_id, channel_id = file.stem.replace(mask_suffix, "").split(channel_prefix)
            if image_id not in id_to_file:
                id_to_file[image_id] = {}

            if channel_id in id_to_file[image_id]:
                raise Exception(
                    f"""The directory already includes a file with the same image and channel ids.
                                Image Id: {image_id}
                                Channel Id: {channel_id}
                                Path: {file}""")

            id_to_file[image_id][channel_id] = file

    #sorting the Channel IDs
    for image_id in id_to_file:
        id_to_file[image_id] = dict(sorted(id_to_file[image_id].items()))
    #sorting the Image IDs
    id_to_file = dict(sorted(id_to_file.items()))
    return id_to_file


def load_directory(directory, bright_field_channel=None, channel_prefix=None, mask_suffix=None):
    assert directory is not None

    if bright_field_channel is None:
        bright_field_channel = 1

    if channel_prefix is None:
        channel_prefix = "c"

    if mask_suffix is None:
        mask_suffix = "_seg"


    names = os.listdir(directory)
    paths = [directory / name for name in names]

    file_paths = [path for path in paths if path.is_file()]

    tiff_files = [path for path in file_paths if path.suffix == ".tif" or path.suffix == ".tiff"]
    # lif_files = [path for path in file_paths if path.suffix == ".lif"]
    mask_files = [path for path in file_paths if path.suffix == ".npy" and path.stem.endswith(mask_suffix)]

    #    if len(lif_files) > 0:
    #        raise Exception("Lif Files are currently not supported.")

    # image_ids = [(file.stem.split(channel_prefix)[0], file) for file in tiff_files]

    id_to_image = organize_files(tiff_files, channel_prefix=channel_prefix)
    id_to_mask = organize_files(mask_files, channel_prefix=channel_prefix, mask_suffix=mask_suffix)

    return id_to_image, id_to_mask
    # raise Exception("Not Implemented Yet")

def copy_files_between_directories(source_dir, target_dir, file_types = None):
    file_filter = lambda file_path: file_path.is_file() and (True if file_types is None else file_path.suffix in file_types)


    files = listdir(source_dir)
    files_to_copy = [file for file in files if file_filter(file)]

    for src_path in files_to_copy:
        target_path = target_dir / src_path.name

        try:
            if target_path.exists():
                if platform.system() == "Windows":
                    os.chmod(target_path, stat.S_IWRITE)
                else:
                    target_path.chmod(0o777)
                target_path.unlink()

            shutil.copy(str(src_path), str(target_path))

        except Exception as e:
            print(f"Something went wrong while processing {src_path.name}: {str(e)}")
            continue

def extract_from_lif_file(lif_path, target_dir,channel_prefix):
    """
    Extracts all series from the lif file using the bioio-lif library and
    copies the images to the target directory.
    Arguments:
          lif_path {str} -- The path to the lif file.
          target_dir {str} -- The path to the target directory.
    """

    lif_path = pathlib.Path(lif_path)
    target_dir = pathlib.Path(target_dir)
    if lif_path.suffix == ".lif":
        bio_image = BioImage(lif_path,reader=bioio_lif.Reader)  # Specify the backend explicitly

        # Create the target directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)

        # get all series in the lif file
        scenes= bio_image.scenes

        for index,scene_id in enumerate(scenes):
            scene= scene_id

            #remove the unnecessary data in the array
            bio_image.set_scene(scene)
            #TCZXY 5D array
            npy_array= bio_image.data
            squeezed_img= np.squeeze(npy_array)

            #get the amount of channels
            n_channels = squeezed_img.shape[0]

            for channel_id in range(n_channels):
                # Extract the height and width of the image
                image= squeezed_img[channel_id]
                img = Image.fromarray(image)#doesnt work

                # Construct file name and path
                file_name = f"{scene}{channel_prefix}{channel_id + 1}.tif"
                target_path = target_dir / file_name

                try:
                    # Handle existing files
                    if target_path.exists():
                        if platform.system() == "Windows":
                            os.chmod(target_path, stat.S_IWRITE)  # Set writable on Windows
                        else:
                            target_path.chmod(0o777)  # Set writable on Unix
                        target_path.unlink()  # Remove the existing file

                    # Save the image to the target path using pillows save function
                    img.save(target_path)

                except Exception as e:
                    print(f"Error processing {file_name}: {e}")
                    continue



def load_image_to_numpy(path):
    im = Image.open(path)
    array = np.array(im)
    return array


def write_numpy_to_image(array, path):
    im = Image.fromarray(array)
    im.save(path)
    pass


def remove_gradient(img):

    """
    The method evens out the background of the images to prone microscopy errors

    Arguments:
        img {PIL.Image} -- The image to be corrected

    """
    top = np.median(img[100:200, 400: -400])
    bottom = np.median(img[-200:-100, 400: -400])

    left = np.median(img[400:-400, 100: 200])
    right = np.median(img[400:-400, -200: -100])

    median = np.median(img[200:-200, 200:-200])

    max_val = np.max([top, bottom, left, right])

    row_count = img.shape[0]

    X = np.arange(row_count) / (row_count - 1)
    b = bottom
    a = top - bottom
    Y_v = a * X + b
    Y_v -= median

    b = right
    a = left - right
    Y_h = a * X + b
    Y_h -= median

    correction_v = np.tile(Y_v, (row_count, 1)).transpose()
    correction_h = np.tile(Y_h, (row_count, 1))
    correction = correction_h + correction_v

    corrected_img = img + correction
    return corrected_img


def transform_image_path(image_path, output_path):
    """
    This method converts images with bit depth of 16 bit to 8 bit

    Attributes:
        image_path (pathlib.Path): Path to the image
        output_path (pathlib.Path): Path where to save the converted image

    Returns:
        True if the image was converted successfully
        False if the image was not converted because it had an incompatible format
    """
    with Image.open(image_path) as img:
        # convert to 8 bit if necessary
        if img.mode == "I;16":
            array16 = np.array(img, dtype=np.uint16)
            array8 = (array16 / 256).astype(np.uint8)
            img8 = Image.fromarray(array8)
            img8.save(output_path, format="TIFF")
            return True
        elif img.mode in ["L", "RGB", "P", "RGBA"]:
            return True
        else:
            return False


def process_channel(channel_id, channel_path):
    image = Image.open(channel_path)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return channel_id, base64.b64encode(buffer.getvalue()).decode('utf-8')

def convert_series_parallel(image_id, cur_image_paths):
    png_images = {image_id: {}}
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(process_channel, channel_id, cur_image_paths[channel_id]): channel_id
            for channel_id in cur_image_paths
        }
        for future in futures:
            channel_id, encoded_image = future.result()
            png_images[image_id][channel_id] = encoded_image

    return png_images

def convert_tiffs_to_png_parallel(image_paths):
    """
    Converts a dict of tiff images to png images using multiprocessing.

    Args:
        image_paths (dict): the dict of image paths of tiff images
    """
    if image_paths is not None:
        png_images = {}
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(convert_series_parallel, image_id, image_paths[image_id]): image_id
                for image_id in image_paths
            }
            for future in futures:
                result = future.result()
                png_images.update(result)

        return png_images
    else:
        return None

def convert_tiffs_to_png(image_paths):
    """
    Converts a dict of tiff images to png images.

    Args:
        image_paths (dict): the dict of image paths of tiff images
    """
    if image_paths is not None:
        png_images = {}
        for image_id in image_paths:
            cur_image_paths = image_paths[image_id]
            if image_id not in png_images:
                png_images[image_id] = {}
            for channel_id in cur_image_paths:
                image = image = Image.open(cur_image_paths[channel_id])

                buffer = BytesIO()
                image.save(buffer, format="PNG")
                buffer.seek(0)

                png_images[image_id][channel_id] = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return png_images
    else:
        return None