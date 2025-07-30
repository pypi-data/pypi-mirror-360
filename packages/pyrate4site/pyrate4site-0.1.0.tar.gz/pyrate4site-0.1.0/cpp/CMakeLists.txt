cmake_minimum_required(VERSION 3.10)
project(rate4site)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -Wno-deprecated -DDOUBLEREP")

# Source files
set(LIB_SOURCES
    AddLog.cpp NNiProp.cpp NNiSep.cpp Nni.cpp aaJC.cpp
    allTrees.cpp allTreesSeparateModel.cpp alphabet.cpp amino.cpp
    bestAlpha.cpp bestAlphaManyTrees.cpp bestHKYparam.cpp bootstrap.cpp
    bblEM.cpp bblEMProprtional.cpp bblEMSeperate.cpp
    chebyshevAccelerator.cpp clustalFormat.cpp codon.cpp codonJC.cpp
    computeCounts.cpp computeDownAlg.cpp computeMarginalAlg.cpp
    computePijComponent.cpp computeUpAlg.cpp computeUpAlgFactors.cpp
    countTableComponent.cpp datMatrixHolder.cpp distanceTable.cpp
    distribution.cpp errorMsg.cpp evaluateCharacterFreq.cpp
    fastStartTree.cpp fastaFormat.cpp findRateOfGene.cpp
    fromCountTableComponentToDistance.cpp
    fromCountTableComponentToDistanceProp.cpp fromQtoPt.cpp
    gammaDistribution.cpp gammaUtilities.cpp generalGammaDistribution.cpp
    getRandomWeights.cpp goldmanYangModel.cpp
    granthamChemicalDistances.cpp hky.cpp khTest.cpp likeDist.cpp
    likeDistProp.cpp likelihoodComputation.cpp
    likelihoodComputationFactors.cpp logFile.cpp maseFormat.cpp
    molphyFormat.cpp nexusFormat.cpp nj.cpp njConstrain.cpp
    nucJC.cpp nucleotide.cpp numRec.cpp phylipFormat.cpp
    pijAccelerator.cpp readDatMatrix.cpp readTree.cpp recognizeFormat.cpp
    replacementModel.cpp searchStatus.cpp seqContainerTreeMap.cpp
    sequence.cpp sequenceContainer.cpp simulateTree.cpp
    siteSpecificRate.cpp someUtil.cpp split.cpp splitMap.cpp
    splitTreeUtil.cpp stochasticProcess.cpp suffStatComponent.cpp
    talRandom.cpp tree.cpp treeIt.cpp treeUtil.cpp uniDistribution.cpp
    uniformDistribution.cpp generalGammaDistributionLaguerre.cpp GLaguer.cpp
    givenRatesMLDistance.cpp distanceBasedSeqs2Tree.cpp
    posteriorDistance.cpp pairwiseGammaDistance.cpp doubleRep.cpp
    indel.cpp indelModel.cpp mulAlphabet.cpp replacementModelSSRV.cpp
    stochasticProcessSSRV.cpp bestAlphaAndNu.cpp  C_evalParamSSRV.cpp
    betaOmegaDistribution.cpp betaUtilities.cpp betaDistribution.cpp geneticCodeHolder.cpp
    bblEM2USSRV.cpp bestParamUSSRV.cpp likeDist2USSRV.cpp ussrvModel.cpp likelihoodComputation2USSRV.cpp
    fromCountTableComponentToDistance2USSRV.cpp normalDist.cpp rate4siteOptions.cpp rate4site.cpp
)

# Create static library
add_library(librate4site STATIC ${LIB_SOURCES})

# Clean target
set_directory_properties(PROPERTIES ADDITIONAL_MAKE_CLEAN_FILES "*.o librate4site.a")
