/*

# $BEGIN_SHADY_LICENSE$
# 
# This file is part of the Shady project, a Python framework for
# real-time manipulation of psychophysical stimuli for vision science.
# 
# Copyright (c) 2017-2025 Jeremy Hill, Scott Mooney
# 
# Shady is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# $END_SHADY_LICENSE$

Include this file as a header for your C or C++ code. See README.txt for more details.

*/

#undef EXTERNC
#if defined __cplusplus && !defined SUPPRESS_EXTERNC
extern "C" {
#define EXTERNC
#endif /* #ifdef __cplusplus */


#define SHADYLIB_MAJOR_VERSION  1  /* NB: Use ShaDyLib_GetVersion(), rather than these       */
#define SHADYLIB_MINOR_VERSION 14  /*     values, to find out the version of the code that   */
#define SHADYLIB_BUILD          0  /*     was used to compile your dynamic library.          */
                                   /*     Verify that the result matches the values here.    */

#define SHADYLIB_VERSION STRINGIFY_VERSION( SHADYLIB_MAJOR_VERSION, SHADYLIB_MINOR_VERSION, SHADYLIB_BUILD )
#define STRINGIFY_VERSION( major, minor, build ) _STRINGIFY( major ) "." STRINGIFY( minor ) "." STRINGIFY( build )
#define  STRINGIFY( s ) _STRINGIFY( s )
#define _STRINGIFY( s ) #s

/* ************************************************************************************ */
#ifndef INCLUDED_ShaDyLib_H
#define INCLUDED_ShaDyLib_H

#include <stddef.h> /* for size_t */
#include <math.h>   /* for INFINITY */
typedef int bool_t;

typedef short          * ShaDyLib_Renderer;
typedef long           * ShaDyLib_Stimulus;
typedef float          * ShaDyLib_RGBTable;
typedef double         * ShaDyLib_Property;
typedef unsigned short * ShaDyLib_PropArray;
typedef unsigned long  * ShaDyLib_Window;

typedef   int  ( *ShaDyLib_MessageCallback )( const char * msg, int debugLevel );
typedef   int  ( *ShaDyLib_UpdateCallback  )( double t, void * ptr );
typedef   void ( *ShaDyLib_EventCallback   )( const char * msg );

extern int Load_ShaDyLib( const char * dllname );

#if defined _WIN32
#  define DYLIB_PREFIX "lib"
#  define DYLIB_EXTENSION ".dll"
#elif defined __APPLE__ 
#  define DYLIB_PREFIX "lib"
#  define DYLIB_EXTENSION ".dylib"
#else
#  define DYLIB_PREFIX "lib"
#  define DYLIB_EXTENSION ".so"
#endif /* #if defined _WIN32 */

#ifndef SHADYLIB_PLATFORM    /*   Define the SHADYLIB_PLATFORM macro when compiling your app to make it easier   */ 
#  define SHADYLIB_PLATFORM  /*   for the app to find the correct build of the dynamic library by default   */
#  define SHADYLIB_DYLIB_NAME( name ) ( ( name ) ? ( name ) : ( DYLIB_PREFIX "Shady" DYLIB_EXTENSION ) )
#else                   /*   Example: if you used the -DSHADYLIB_PLATFORM=-Darwin-x86_64 compiler flag then SHADYLIB_DYLIB_NAME( NULL ) would expand to "libShady-Darwin-x86_64.dylib"   */
#  define SHADYLIB_DYLIB_NAME( name ) ( ( name ) ? ( name ) : ( DYLIB_PREFIX "Shady" STRINGIFY( SHADYLIB_PLATFORM ) DYLIB_EXTENSION ) )
#endif /* #ifndef SHADYLIB_PLATFORM */
#ifndef SHADYLIB_FUNC
#  ifdef SHADYLIB_STATIC
#    define SHADYLIB_FUNC( type, name, args, implementation )  type name  args; /* required if linking statically against ShaDyLib_C_Interface.cpp */
#  else
#    define SHADYLIB_FUNC( type, name, args, implementation )  extern type ( *name ) args;  /* required if linking dynamically (default, normal use-case) */
#  endif /* #ifdef SHADYLIB_STATIC */
#endif /* #ifndef SHADYLIB_FUNC */

#endif /* #ifndef INCLUDED_ShaDyLib_H */
/* ************************************************************************************ */
/* ************************************************************************************ */


/* **************************************************** */
/* General-purpose functions                            */
/* **************************************************** */

SHADYLIB_FUNC(  const char *      ,    ShaDyLib_Error                                     ,  ( void )                                                                 ,   { return gShaDyLibErrorString; }                                                                              )
SHADYLIB_FUNC(  const char *      ,    ShaDyLib_ClearError                                ,  ( void )                                                                 ,   { const char * p = gShaDyLibErrorString; gShaDyLibErrorString = NULL; return p; }                             )
SHADYLIB_FUNC(  void              ,    ShaDyLib_SetErrorCallback                          ,  ( ShaDyLib_MessageCallback func )                                        ,   { gShaDyLibErrorHandler = func; }                                                                             )

SHADYLIB_FUNC(  void              ,    ShaDyLib_SanityCheck                               ,  ( void )                                                                 ,   DO( ShaDyLib::SanityCheck(); )                                                                                )
SHADYLIB_FUNC(  int               ,    ShaDyLib_Console                                   ,  ( const char * msg, int debugLevel )                                     ,   RETURN( 0, DebuggingUtils::Console( INPUTSTRING( msg ), debugLevel ) )                                        )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Sleep                                     ,  ( double seconds )                                                       ,   DO( TimeUtils::SleepSeconds( seconds ) )                                                                      )
SHADYLIB_FUNC(  const char *      ,    ShaDyLib_PythonString                              ,  ( const void * raw, size_t nBytes, bool_t allhex )                       ,   RETURNSTRING( StringUtils::StringRepresentation( ( const char * )raw, nBytes, allhex ) )                      )

SHADYLIB_FUNC(  const char *      ,    ShaDyLib_GetPlatform                               ,  ( void )                                                                 ,   RETURNSTRING( ShaDyLib::GetPlatform() )                                                                       )
SHADYLIB_FUNC(  const char *      ,    ShaDyLib_GetCompilationDatestamp                   ,  ( void )                                                                 ,   RETURNSTRING( ShaDyLib::GetCompilationDatestamp() )                                                           )
SHADYLIB_FUNC(  const char *      ,    ShaDyLib_GetRevision                               ,  ( void )                                                                 ,   RETURNSTRING( ShaDyLib::GetRevision() )                                                                       )
SHADYLIB_FUNC(  const char *      ,    ShaDyLib_GetVersion                                ,  ( void )                                                                 ,   RETURNSTRING( SHADYLIB_VERSION )                                                                              )
SHADYLIB_FUNC(  const char *      ,    ShaDyLib_GetOpenGLVersion                          ,  ( void )                                                                 ,   RETURNSTRING( ShaDyLib::GetOpenGLVersion() )                                                                  )
SHADYLIB_FUNC(  const char *      ,    ShaDyLib_GetGLSLVersion                            ,  ( void )                                                                 ,   RETURNSTRING( ShaDyLib::GetGLSLVersion() )                                                                    )

SHADYLIB_FUNC(  ShaDyLib_Renderer ,    ShaDyLib_Renderer_New                              ,  ( unsigned int shaderProgram, bool_t legacy )                            ,   RETURN( NULL, ( ShaDyLib_Renderer )new ShaDyLib::Renderer( shaderProgram, legacy ) )                          )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Renderer_Delete                           ,  ( ShaDyLib_Renderer r )                                                  ,   DO( delete RENDERER )                                                                                         )
SHADYLIB_FUNC(  ShaDyLib_Stimulus ,    ShaDyLib_Renderer_CreateStimulus                   ,  ( ShaDyLib_Renderer r, const char * name )                               ,   RETURN( NULL, ( ShaDyLib_Stimulus ) RENDERER->CreateStimulus( INPUTSTRING( name ) ) )                         )
SHADYLIB_FUNC(  ShaDyLib_RGBTable ,    ShaDyLib_Renderer_CreateRGBTable                   ,  ( ShaDyLib_Renderer r )                                                  ,   RETURN( NULL, ( ShaDyLib_RGBTable ) RENDERER->CreateRGBTable() )                                              )
SHADYLIB_FUNC(  ShaDyLib_Property ,    ShaDyLib_Renderer_GetProperty                      ,  ( ShaDyLib_Renderer r, const char * name )                               ,   RETURN( NULL, ( ShaDyLib_Property ) RENDERER->Properties( INPUTSTRING( name ), true ) )                       )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Renderer_SetUpdateCallback                ,  ( ShaDyLib_Renderer r, ShaDyLib_UpdateCallback func, void * userPtr )    ,   DO( RENDERER->SetUpdateCallback( func, userPtr ) )                                                            )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Renderer_Draw                             ,  ( ShaDyLib_Renderer r )                                                  ,   DO( RENDERER->Draw() )                                                                                        )
SHADYLIB_FUNC(  ShaDyLib_Property ,    ShaDyLib_Renderer_MakeCustomUniform                ,  ( ShaDyLib_Renderer r, const char * name, unsigned int numberOfElements, int floatingPoint ) , RETURN( NULL, ( ShaDyLib_Property ) RENDERER->CreateCustomUniform( INPUTSTRING( name ), numberOfElements, floatingPoint ) )         )
SHADYLIB_FUNC(  ShaDyLib_PropArray ,   ShaDyLib_Renderer_CreatePropertyArray              ,  ( ShaDyLib_Renderer r, const char * property, const char * stimuli )     ,   RETURN( NULL, ( ShaDyLib_PropArray ) new ShaDyLib::PropArray( RENDERER, INPUTSTRING( property ), INPUTSTRING( stimuli ) ) )        )

SHADYLIB_FUNC(  double            ,    ShaDyLib_Renderer_Seconds                          ,  ( ShaDyLib_Renderer r )                                                  ,   RETURN( 0, RENDERER->Seconds() )                                                                              )
//SHADYLIB_FUNC(  int               ,    ShaDyLib_Renderer_GetNumberOfTextureSlots          ,  ( ShaDyLib_Renderer r )                                                  ,   RETURN( 0, ShaDyLib::GetNumberOfTextureSlots() )                                                              )
SHADYLIB_FUNC(  int               ,    ShaDyLib_Renderer_QueryDACMax                      ,  ( ShaDyLib_Renderer r )                                                  ,   RETURN( 0, RENDERER->QueryDACMax() )                                                                          )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Renderer_CaptureRawRGBA                   ,  ( ShaDyLib_Renderer r, int left, int bottom, int width, int height, char * buffer )  ,  DO( ShaDyLib::CaptureRawRGBA( left, bottom, width, height, buffer ) )                              )
SHADYLIB_FUNC(  int               ,    ShaDyLib_Renderer_CaptureToTexture                 ,  ( ShaDyLib_Renderer r, int left, int bottom, int width, int height, int destTextureID )  ,  RETURN( -1, RENDERER->CaptureToTexture( left, bottom, width, height, destTextureID ) )         )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Renderer_SetSwapInterval                  ,  ( ShaDyLib_Renderer r, int value, int glfw )                             ,   DO( ShaDyLib::SetSwapInterval( value, glfw != 0 ) )                                                           )
SHADYLIB_FUNC(  const char *      ,    ShaDyLib_Renderer_GetStimulusOrder                 ,  ( ShaDyLib_Renderer r )                                                  ,   RETURN( NULL, RENDERER->GetStimulusOrder() ) /* it's ok not to use RETURNSTRING in this particular case */    )
SHADYLIB_FUNC(  const char *      ,    ShaDyLib_Renderer_GetUpdatedKeys                   ,  ( ShaDyLib_Renderer r )                                                  ,   RETURNSTRING( RENDERER->GetUpdatedKeys() )                                                                    )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Renderer_EnableCulling                    ,  ( ShaDyLib_Renderer r, double alphaThreshold )                           ,   DO( RENDERER->EnableCulling( alphaThreshold ) )                                                               )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Renderer_DisableCulling                   ,  ( ShaDyLib_Renderer r )                                                  ,   DO( RENDERER->DisableCulling() )                                                                              )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Renderer_DisableShadyPipeline             ,  ( ShaDyLib_Renderer r )                                                  ,   DO( RENDERER->DisableShadyPipeline() )                                                                        )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Renderer_WaitForFrames                    ,  ( ShaDyLib_Renderer r, int policy )                                      ,   DO( RENDERER->mWaitForFrames = policy )                                                                       )

SHADYLIB_FUNC(  unsigned int      ,    ShaDyLib_InitShading                               ,  ( unsigned int width, unsigned int height, const char * glslDirectory, const char * substitutions )  ,   RETURN( 0, ShaDyLib::InitShading( width, height, INPUTSTRING( glslDirectory ), INPUTSTRING( substitutions ) ) )                             )

SHADYLIB_FUNC(  ShaDyLib_Property ,    ShaDyLib_Stimulus_GetProperty                      ,  ( ShaDyLib_Stimulus s, const char * name )                               ,   RETURN( NULL, ( ShaDyLib_Property ) STIMULUS->Properties( INPUTSTRING( name ), true ) )                       )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Stimulus_Draw                             ,  ( ShaDyLib_Stimulus s )                                                  ,   DO( STIMULUS->Draw() )                                                                                        )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Stimulus_LoadTexture                      ,  ( ShaDyLib_Stimulus s, int width, int height, int nChannels, const char * dataType, void * data ) , DO( STIMULUS->LoadTexture( width, height, nChannels, dataType, data ) )                )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Stimulus_LoadSubTexture                   ,  ( ShaDyLib_Stimulus s, int column, int row, int width, int height, int nChannels, const char * dataType, void * data ) , DO( STIMULUS->LoadSubTexture( column, row, width, height, nChannels, dataType, data ) )        )
SHADYLIB_FUNC(  int               ,    ShaDyLib_Stimulus_SetLinearMagnification           ,  ( ShaDyLib_Stimulus s, int setting )                                     ,   RETURN( 0, ( int )STIMULUS->SetLinearMagnification( setting ) )                                               )
SHADYLIB_FUNC(  ShaDyLib_Property ,    ShaDyLib_Stimulus_MakeCustomUniform                ,  ( ShaDyLib_Stimulus s, const char * name, unsigned int numberOfElements, int floatingPoint ) , RETURN( NULL, ( ShaDyLib_Property ) STIMULUS->CreateCustomUniform( INPUTSTRING( name ), numberOfElements, floatingPoint ) )         )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Stimulus_Enter                            ,  ( ShaDyLib_Stimulus s )                                                  ,   DO( STIMULUS->Enter() )                                                                                       )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Stimulus_Leave                            ,  ( ShaDyLib_Stimulus s )                                                  ,   DO( STIMULUS->Leave() )                                                                                       )

SHADYLIB_FUNC(  ShaDyLib_Property ,    ShaDyLib_RGBTable_GetProperty                      ,  ( ShaDyLib_RGBTable t, const char * name )                               ,   RETURN( NULL, ( ShaDyLib_Property ) RGBTABLE->Properties( INPUTSTRING( name ), true ) )                       )
SHADYLIB_FUNC(  void              ,    ShaDyLib_RGBTable_LoadTexture                      ,  ( ShaDyLib_RGBTable t, int width, int height, int nChannels, const char * dataType, void * data ) , DO( RGBTABLE->LoadTexture( width, height, nChannels, dataType, data ) )                )

SHADYLIB_FUNC(  void *            ,    ShaDyLib_Property_GetDataPointer                   ,  ( ShaDyLib_Property p )                                                  ,   RETURN( NULL, PROPERTY->GetDataPointer() )                                                                    )
SHADYLIB_FUNC(  const char *      ,    ShaDyLib_Property_GetDataType                      ,  ( ShaDyLib_Property p )                                                  ,   RETURNSTRING( PROPERTY->GetDataType() )                                                                       )
SHADYLIB_FUNC(  int               ,    ShaDyLib_Property_GetNumberOfElements              ,  ( ShaDyLib_Property p )                                                  ,   RETURN( 0, PROPERTY->GetNumberOfElements() )                                                                  )
SHADYLIB_FUNC(  int               ,    ShaDyLib_Property_GetUniformAddress                ,  ( ShaDyLib_Property p )                                                  ,   RETURN( 0, PROPERTY->GetUniformAddress() )                                                                    )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Property_LinkWithMaster                   ,  ( ShaDyLib_Property p, ShaDyLib_Property master )                        ,   DO( PROPERTY->LinkWithMaster( ( ShaDyLib::Property * ) master ) )                                             )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Property_CopyValueFrom                    ,  ( ShaDyLib_Property p, ShaDyLib_Property master )                        ,   DO( PROPERTY->CopyValueFrom( ( ShaDyLib::Property * ) master ) )                                              )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Property_MakeIndependent                  ,  ( ShaDyLib_Property p, int revertValue )                                 ,   DO( PROPERTY->MakeIndependent( revertValue ) )                                                                )

SHADYLIB_FUNC(  void              ,    ShaDyLib_PropArray_Delete                          ,  ( ShaDyLib_PropArray a )                                                 ,   DO( delete ARRAY )                                                                                            )
SHADYLIB_FUNC(  void *            ,    ShaDyLib_PropArray_GetDataPointer                  ,  ( ShaDyLib_PropArray a )                                                 ,   RETURN( NULL, ARRAY->GetDataPointer() )                                                                       )
SHADYLIB_FUNC(  const char *      ,    ShaDyLib_PropArray_GetDataType                     ,  ( ShaDyLib_PropArray a )                                                 ,   RETURNSTRING( ARRAY->GetDataType() )                                                                          )
SHADYLIB_FUNC(  size_t            ,    ShaDyLib_PropArray_GetNumberOfStimuli              ,  ( ShaDyLib_PropArray a )                                                 ,   RETURN( 0, ARRAY->GetNumberOfStimuli() )                                                                      )
SHADYLIB_FUNC(  size_t            ,    ShaDyLib_PropArray_GetNumberOfColumns              ,  ( ShaDyLib_PropArray a )                                                 ,   RETURN( 0, ARRAY->GetNumberOfColumns() )                                                                      )

SHADYLIB_FUNC(  const char *      ,    ShaDyLib_Screens                                   ,  ( int pythonFormat)                                                      ,   RETURNSTRING( ShaDyLib::Screens( pythonFormat ) )                                                             )

SHADYLIB_FUNC(  ShaDyLib_Window   ,    ShaDyLib_Window_New                                ,  ( int width, int height, int left, int top, int screen, int frame, double fullScreenMode, int visible, int overlayMode, int openglContextVersion, int legacy, const char * glslDirectory, const char * substitutions )  ,   RETURN( NULL, ( ShaDyLib_Window )new ShaDyLib::Window( width, height, left, top, screen, frame, fullScreenMode, visible, overlayMode, openglContextVersion, legacy, INPUTSTRING( glslDirectory ), INPUTSTRING( substitutions ) ) )       )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Window_Delete                             ,  ( ShaDyLib_Window w )                                                    ,   DO( delete WINDOW )                                                                                           )
SHADYLIB_FUNC(  ShaDyLib_Renderer ,    ShaDyLib_Window_GetRenderer                        ,  ( ShaDyLib_Window w )                                                    ,   RETURN( NULL, ( ShaDyLib_Renderer) WINDOW->GetRenderer() )                                                    )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Window_SetEventCallback                   ,  ( ShaDyLib_Window w, ShaDyLib_EventCallback func )                       ,   DO( WINDOW->SetEventCallback( func ) )                                                                        )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Window_SetPixelScaling                    ,  ( ShaDyLib_Window w, double ratio )                                      ,   DO( WINDOW->SetPixelScaling( ratio ) )                                                                        )
SHADYLIB_FUNC(  int               ,    ShaDyLib_Window_GetWidth                           ,  ( ShaDyLib_Window w )                                                    ,   RETURN( 0, WINDOW->GetWidth() )                                                                               )
SHADYLIB_FUNC(  int               ,    ShaDyLib_Window_GetHeight                          ,  ( ShaDyLib_Window w )                                                    ,   RETURN( 0, WINDOW->GetHeight() )                                                                              )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Window_Run                                ,  ( ShaDyLib_Window w )                                                    ,   DO( WINDOW->Run() )                                                                                           )
SHADYLIB_FUNC(  void              ,    ShaDyLib_Window_Close                              ,  ( ShaDyLib_Window w )                                                    ,   DO( WINDOW->Close() )                                                                                         )


/* ************************************************************************************ */
/* ************************************************************************************ */
#ifdef EXTERNC
} /* ends extern "C" block */
#endif /* #ifdef EXTERNC */
#undef SHADYLIB_FUNC
