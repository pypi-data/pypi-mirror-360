from bitbox.face_backend import FaceProcessor3DI as FP

input_file = 'data/elaine.mp4'
output_dir = 'output'

# define a face processor
processor = FP()

# set input and output
processor.io(input_file=input_file, output_dir=output_dir)

# detect faces
rects = processor.detect_faces()

# detect landmarks
lands = processor.detect_landmarks()

# compute global expressions
exp_global, pose, lands_can = processor.fit()

# compute localized expressions
exp_local = processor.localized_expressions()