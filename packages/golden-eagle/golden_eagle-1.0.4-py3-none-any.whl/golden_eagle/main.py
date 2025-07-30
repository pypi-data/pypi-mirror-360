import cv2
import face_recognition
import gc
import numpy as np
import numpy.typing as npt
import os
import traceback

from typing import ClassVar
from typing import Optional
from pydantic import BaseModel


class Compare(BaseModel):
    before: ClassVar[list]
    after: ClassVar[list]
    before_enc: ClassVar[list]
    after_enc: ClassVar[list]
    en_loc_before: ClassVar[list]
    en_before: ClassVar[list]
    en_loc_after: ClassVar[list]
    en_after: ClassVar[list]
    tolerance: ClassVar[float]
    results: ClassVar[list]
    face_d: ClassVar[npt.NDArray]
    hyoka: ClassVar[npt.DTypeLike]


# face compare to myself_(before and after)
def compare_before_after(before, after):
    # pydantic syntax check, true || false
    Compare == before
    Compare == after

    # This is myself before and after picture.
    before_enc = cv2.cvtColor(before, cv2.COLOR_BGR2RGB)
    after_enc = cv2.cvtColor(after, cv2.COLOR_BGR2RGB)

    # pydantic syntax check, true || false
    Compare == before_enc
    Compare == after_enc

    # A list of 128-dimensional face recognition before encode
    # Which face detection model to use.
    # “hog” is less accurate but faster on CPUs.
    # “cnn” is a more accurate deep-learning model,
    # which is GPU/CUDA accelerated (if available).
    en_loc_before = face_recognition.face_locations(before_enc, model='cnn')[0]
    en_before = face_recognition.face_encodings(before_enc)[0]
    cv2.rectangle(before, (en_loc_before[3], en_loc_before[0]),
                  (en_loc_before[1], en_loc_before[2]), (255, 0, 255), 2)

    # pydantic syntax check, true || false
    Compare == en_loc_before
    Compare == en_before

    # A list of 128-dimensional face recognition after encode
    # The default is “hog”.
    # https://face-recognition.readthedocs.io/en/latest/face_recognition.html
    en_loc_after = face_recognition.face_locations(after_enc, model='cnn')[0]
    en_after = face_recognition.face_encodings(after_enc)[0]
    cv2.rectangle(after, (en_loc_after[3], en_loc_after[0]),
                  (en_loc_after[1], en_loc_after[2]), (255, 0, 255), 2)

    # pydantic syntax check, true || false
    Compare == en_loc_after
    Compare == en_after

    # https://face-recognition.readthedocs.io/en/latest/readme.html
    # You can do that with the --tolerance parameter. The default tolerance
    # value is 0.6 and lower numbers make face comparisons more strict:
    tolerance: Optional[float] = 0.32

    # [np.True_] | [np.Flase]
    results: Optional[list] = face_recognition.compare_faces(
        [en_before], en_after, tolerance=tolerance)

    # pydantic syntax check, true || false
    Compare == tolerance
    Compare == results

    # The data is processed as a feature quantity.
    face_d: npt.NDArray = face_recognition.face_distance([en_before], en_after)
    hyoka: npt.DTypeLike = (np.floor(face_d * 1000).astype(int) / 1000)

    # pydantic syntax check, true || false
    Compare == face_d
    Compare == hyoka

    # Add exception handling.
    try:
        # A return value of 0.31 or less is expected.
        if results[0]:
            print("accuracy:" + str(hyoka) + " " + "⭕️")

            # return code, before and after.
            return *before, *after

        # Values of 0.32 or higher are expected.
        elif not results[0]:
            print("accuracy:" + str(hyoka) + " " + "❎️")
            # Unique exception occurrence.
            raise ValueError("Use a recent photo of your face.")

        # Usually not reached.
        else:
            # Unique exception occurrence.
            raise ValueError("Please check the passcode for your face photo.")

    # TraceBack.
    except Exception:
        # Specify the folder to record the exception log.
        except_folder: Optional[str] = os.getcwd()
        # Specify the file to log exception occurrences.
        except_file: Optional[str] = os.getcwd() + '.log'

        # Load the dictionary.
        if os.path.isdir(os.path.expanduser(except_folder)):
            # Log writing process.
            with open(os.path.expanduser(except_file), 'a') as log_py:
                traceback.print_exc(file=log_py)

                # throw except.
                raise RuntimeError from None

        # Current directory Not Found.
        else:
            # Unique exception occurrence.
            raise ValueError("None, Please Check the Current directory.")

    # Once Exec.
    finally:
        # GC collection.
        gc.collect()
