//
// Inputs
//
Inputs
{
	Mat source0;
}

//
// Variables
//
Outputs
{
	Mat cvThresholdOutput;
}

//
// Steps
//

Step CV_Threshold0
{
    Mat cvThresholdSrc = source0;
    Double cvThresholdThresh = 50.0;
    Double cvThresholdMaxval = 0;
    ThresholdType cvThresholdType = THRESH_TRUNC;

    cvThreshold(cvThresholdSrc, cvThresholdThresh, cvThresholdMaxval, cvThresholdType, cvThresholdOutput);
}




