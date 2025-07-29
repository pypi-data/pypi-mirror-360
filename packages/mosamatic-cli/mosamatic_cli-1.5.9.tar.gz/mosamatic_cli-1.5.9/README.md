# mosamatic-cli
Command-line tool for running processing tasks on medical images

# To-do
- NumPy to NIFTI conversion

- Create PNG images from DICOM files

- Slice selection using either Total Segmentator or MOOSE

  What you can do is first create spinal segmentations of a CT scan. Then
  you can use that data to pick a segmentation, e.g., the L3 vertebra and
  select the middle slice. In terms of commands/tasks, this would mean a
  command/task:
  - SegmentAnatomyTS: with option to output a specific segmentation object
  - SegmentAnatomyMOOSE: with option to output a specific segmentation 
    object
  - SelectSlice: Given a CT scan and a segmentation object, select the 
    middle or other slice

- CT/MRI registration using ANTsPy

- IMAT analysis

  Discuss with Leroy how to detect fat inside muscle (either as SAT or 
  black pixels). If pixels inside muscle are black, what does that mean?
  Can I overlay the mask on top of the image and check the pixel gray
  values and then determine (using the Alberta threshold range) whether
  these pixels are fat or not?

- Calculate muscle PDFF maps from Dixon MRI after registering with CT

# Next action
- Implement slice selection with Total Segmentator