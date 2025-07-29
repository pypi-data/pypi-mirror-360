// Copyright (C) 2025 Université de Reims Champagne-Ardenne.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
//     (1) Redistributions of source code must retain the above copyright
//     notice, this list of conditions and the following disclaimer.
//
//     (2) Redistributions in binary form must reproduce the above copyright
//     notice, this list of conditions and the following disclaimer in
//     the documentation and/or other materials provided with the
//     distribution.
//
//     (3)The name of the author may not be used to
//     endorse or promote products derived from this software without
//     specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
// IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
// INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
// HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
// STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
// IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.

#ifndef EEGVIZLIB_HEADER_INCLUDED
# define EEGVIZLIB_HEADER_INCLUDED

# include <stddef.h>
# include <stdint.h>

# include <SDL2/SDL.h>

# define EEGVIZLIB_IS_SHARED_OBJECT 1

# if HAVE_VISIBILITY && EEGVIZLIB_IS_SHARED_OBJECT && BUILDING_LIBEEGVIZ
#  define LIBEEGVIZ_SHLIB_EXPORTED __attribute__((__visibility__("default")))
# elif (defined _WIN32 && !defined __CYGWIN__) && EEGVIZLIB_IS_SHARED_OBJECT && BUILDING_LIBEEGVIZ
#  if defined DLL_EXPORT
#   define LIBEEGVIZ_SHLIB_EXPORTED __declspec(dllexport)
#  else
#   define LIBEEGVIZ_SHLIB_EXPORTED
#  endif
# elif (defined _WIN32 && !defined __CYGWIN__) && EEGVIZLIB_IS_SHARED_OBJECT
#  define LIBEEGVIZ_SHLIB_EXPORTED __declspec(dllimport)
# else
#  define LIBEEGVIZ_SHLIB_EXPORTED
# endif

# ifdef __cplusplus
extern "C"
{
# endif				/* __cplusplus */

  struct eegviz;

  extern LIBEEGVIZ_SHLIB_EXPORTED struct eegviz *eegviz_alloc (void);
  extern LIBEEGVIZ_SHLIB_EXPORTED void eegviz_free (struct eegviz *eegviz);
  extern LIBEEGVIZ_SHLIB_EXPORTED
    int eegviz_setup_sdl (struct eegviz *viz, SDL_Renderer * renderer);

  extern LIBEEGVIZ_SHLIB_EXPORTED
    int eegviz_open (struct eegviz *viz, const char *filename);

  extern LIBEEGVIZ_SHLIB_EXPORTED
    int eegviz_sdl_change_renderer (struct eegviz *viz,
				    SDL_Renderer * renderer);
  extern LIBEEGVIZ_SHLIB_EXPORTED int eegviz_render (struct eegviz *viz);
  extern LIBEEGVIZ_SHLIB_EXPORTED int eegviz_shall_quit (struct eegviz *viz);

  /* These descriptions are those of trame */
  extern LIBEEGVIZ_SHLIB_EXPORTED
    int eegviz_key_press (struct eegviz *viz, const char *key_description);
  extern LIBEEGVIZ_SHLIB_EXPORTED
    int eegviz_pointer_move (struct eegviz *view, double x, double y);
  extern LIBEEGVIZ_SHLIB_EXPORTED int eegviz_primary (struct eegviz *view);
  extern LIBEEGVIZ_SHLIB_EXPORTED int eegviz_secondary (struct eegviz *view);

  /* This is not thread-safe, not reentrant. */
  extern LIBEEGVIZ_SHLIB_EXPORTED
    int eegviz_set_relocation_prefix (const char *expected,
				      const char *observed);

  /* This is thread-safe and reentrant. */
  extern LIBEEGVIZ_SHLIB_EXPORTED
    const char *eegviz_relocate (const char *source, char **allocated);

  /* Should be PyObject *, but I don’t want to include the whole
     Python includes here. */
  extern LIBEEGVIZ_SHLIB_EXPORTED void *PyInit_libeegviz (void);

# ifdef __cplusplus
}
# endif				/* __cplusplus */
#endif				/* not EEGVIZLIB_HEADER_INCLUDED */
