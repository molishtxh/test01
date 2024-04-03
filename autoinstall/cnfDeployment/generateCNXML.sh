#!/bin/bash

SCRIPTHOME=$(dirname $0)

YANG_FOLDER=$1
shift
GENERIC_XML=$SCRIPTHOME/../../CONFIGURATION/cms-8200-hss-nt-hlr_nds_generic.xml
RESULT=$YANG_FOLDER.xml


LDAPBACKEND=nds
TEMPLATECHECK=true

if [ -z "$YANG_FOLDER" ]; then
  echo "ERROR: No yang folder specified." >&2
  echo "  Usage: $0 <yang folder> [<key>=<value> [<key>=<value> [ ... ] ] ]" >&2
  echo "Output will be saved into <yang folder>.xml" >&2
  echo "Special keys:" >&2
  echo "  ldapbackend=<nds|sdl>" >&2
  echo "  templatecheck=<true|false>" >&2
  exit 1
fi

while [ -n "$1" ]; do
  KEY=$(echo $1 | cut -d = -f 1)
  VALUE=$(echo $1 | cut -d = -f 2)
  if [ "$KEY" == "ldapbackend" ]; then
    LDAPBACKEND=$VALUE
  elif [ "$KEY" == "templatecheck" ]; then
    TEMPLATECHECK=$VALUE
  else
    SEDEXPRESSION+=" -e 's/##$KEY##/$VALUE/'"
  fi
  shift
done

if [ "$LDAPBACKEND" = "sdl" ];then
  SEDEXPRESSION+=" -e '/<!--NDS parameters start-->/,/<!--NDS parameters end-->/d'"
  SEDEXPRESSION+=" -e '/<!--SDL parameters/d'"
else
  SEDEXPRESSION+=" -e '/<!--SDL parameters start-->/,/<!--SDL parameters end-->/d'"
  SEDEXPRESSION+=" -e '/<!--NDS parameters/d'"
fi

eval sed $SEDEXPRESSION $GENERIC_XML > $RESULT

if $TEMPLATECHECK; then
  TEMPLATES=$(grep -n '##' $RESULT)
  if [ -n "$TEMPLATES" ]; then
    echo "ERROR: templates remained in the following lines in $RESULT:" >&2
    echo "$TEMPLATES"
    exit 1
  fi
fi
