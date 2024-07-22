
from ..import __package__ as __main__
if __main__.__contains__('sculpt_paint_wheel'):
    from enum import Enum

    CF_VS = """
  uniform mat4 ModelViewProjectionMatrix;
  uniform float size;

  in vec2 p;

  void main()
  {
    gl_Position = ModelViewProjectionMatrix * vec4(p, 1.0, 1.0);
    gl_PointSize = size;
  }
  """

    CF_FS = """
  uniform vec4 co;
  out vec4 fragColor;

  float circleshape(vec2 _pos, float _radius){
      return step(_radius, length(_pos - vec2(0.5)));
  }

  void main()
  {
    float a = circleshape(gl_PointCoord, .5);

    if (a == 1.0) {
      discard;
    }

    fragColor = vec4(co, a);
    fragColor.rgb = pow(fragColor.rgb, vec3(2.2));
  }
  """

    # 2nd method.
    # float roundedFrame(float d, float thickness)
    # {
    #   return smoothstep(0.55, 0.45, abs(d / thickness) * 5.0);
    # }
    CFS2_FS = """
  uniform vec4 co;
  out vec4 fragColor;

  void main()
  {
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    float rad = dot(cxy, cxy);

    float alpha = smoothstep(0.55, 0.45, abs(rad / 9.5) * 5.0);
    if (alpha < 0.05)
      discard;
    fragColor = co;
    fragColor.a *= alpha;
  }
  """ # pow(fragColor.rgb, vec3(2.2));

  # 2nd method.
    CFS2_GAMMA_FS = """
  uniform vec4 co;
  out vec4 fragColor;

  float roundedFrame (float d, float thickness)
  {
    return smoothstep(0.55, 0.45, abs(d / thickness) * 5.0);
  }

  void main()
  {
    float r = 0.0;
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    r = dot(cxy, cxy);

    float s = roundedFrame(r, 9.5);
    if (s < 0.05)
      discard;
    fragColor = co;
    fragColor.a *= s;
    fragColor.rgb = pow(fragColor.rgb, vec3(2.2));
  }
  """

    CFS_CROPTOP_FS = """
  uniform vec4 co;
  out vec4 fragColor;

  float roundedFrame (float d, float thickness)
  {
    return smoothstep(0.55, 0.45, abs(d / thickness) * 5.0);
  }

  void main()
  {
    float r = 0.0;
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    
    if (cxy.y <= 0.5)
      discard;
    
    r = dot(cxy, cxy);

    float s = roundedFrame(r, 9.5);
    if (s < 0.05)
      discard;
    fragColor = co;
    fragColor.a *= s;
  }
  """

    CFS_CROPBOT_FS = """
  uniform vec4 co;
  out vec4 fragColor;

  float roundedFrame (float d, float thickness)
  {
    return smoothstep(0.55, 0.45, abs(d / thickness) * 5.0);
  }

  void main()
  {
    float r = 0.0;
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    
    if (cxy.y >= 0.5)
      discard;
    
    r = dot(cxy, cxy);

    float s = roundedFrame(r, 9.5);
    if (s < 0.05)
      discard;
    fragColor = co;
    fragColor.a *= s;
  }
  """

    ###################
    ###################
    # IMG
    IMG_VS = '''
      uniform mat4 ModelViewProjectionMatrix;

      in vec2 texco;
      in vec2 p;
      out vec2 texco_interp;

      void main()
      {
          gl_Position = ModelViewProjectionMatrix * vec4(p, 1.0f, 1.0f);
          texco_interp = texco;
      }
  '''
    IMGA_FS = '''
      in vec2 texco_interp;
      out vec4 fragColor;

      uniform sampler2D image;

      void main()
      {
          vec4 texColor = texture(image, texco_interp);
          if(texColor.a < 0.05)
              discard;

          fragColor = texColor;
      }
  '''
    IMGA_GAMMCORR_FS = '''
  uniform sampler2D image;
  in vec2 texco_interp;
  out vec4 fragColor;

  float linearrgb_to_srgb(float c)
  {
    if (c < 0.0031308) {
      return (c < 0.0) ? 0.0 : c * 12.92;
    }
    else {
      return 1.055 * pow(c, 1.0 / 2.4) - 0.055;
    }
  }

  void linearrgb_to_srgb(vec4 col_from, out vec4 col_to)
  {
    col_to.r = linearrgb_to_srgb(col_from.r);
    col_to.g = linearrgb_to_srgb(col_from.g);
    col_to.b = linearrgb_to_srgb(col_from.b);
    col_to.a = col_from.a;
  }

  void main()
  {
    //smoothstep(.5-1.0, .5+1.0, distance(texco_interp, vec2(.5f)));
    float dist = length(vec2(.5f)-texco_interp);
    if (dist > .5f)
      discard;
    fragColor = texture(image, texco_interp);
    //linearrgb_to_srgb(fragColor, fragColor);
    if (dist > .4f)
      fragColor.a *= smoothstep(.5f, .4f, dist);
    //fragColor = blender_srgb_to_framebuffer_space(fragColor);
    //fragColor.rgb = pow(fragColor.rgb, vec3(2.2));
  }
  '''
    '''
    in vec2 texco_interp;
    out vec4 fragColor;

    uniform sampler2D image;

    void main()
    {
      vec4 texColor = texture(image, texco_interp);
      if(texColor.a < 0.05)
        discard;

      fragColor.rgb = pow(texColor.rgb, vec3(.454545));
      fragColor.a = texColor.a;
    }
  '''

    IMGA_GAMMA_OP = '''
    in vec2 texco_interp;
    out vec4 fragColor;

    uniform sampler2D image;
    uniform float o;

    void main()
    {
      vec4 texColor = texture(image, texco_interp);
      if(texColor.a < 0.05)
          discard;

      fragColor.rgb = pow(texColor.rgb, vec3(.454545));
      fragColor.a = texColor.a * o;
    }
  '''

    IMGA_GAMMCORR_BOOST_FS = """
    in vec2 texco_interp;
    out vec4 fragColor;

    uniform sampler2D image;
    uniform float boost;

    // All components are in the range [0…1], including hue.
    vec3 rgb2hsv(vec3 c)
    {
      vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
      vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
      vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

      float d = q.x - min(q.w, q.y);
      float e = 1.0e-10;
      return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
    }

    // All components are in the range [0…1], including hue.
    vec3 hsv2rgb(vec3 c)
    {
      vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
      vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
      return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
    }

    void main()
    {
      float dist = length(vec2(.5f)-texco_interp);
      if (dist > .5f)
        discard;
      vec4 texColor = texture(image, texco_interp);
      if(texColor.a < 0.05)
          discard;
      texColor = vec4(pow(texColor.rgb, vec3(.454545)), texColor.a);
      texColor.rgb = rgb2hsv(texColor.rgb);
      texColor.gb *= boost;
      fragColor.rgb = hsv2rgb(texColor.rgb);
      fragColor.a = texColor.a;
      if (dist > .4f)
        fragColor.a *= smoothstep(.5f, .4f, dist);
    }
  """

    PLIGHT_FS = """
  uniform vec3 co;
  out vec4 fragColor;
  void main()
  {
    float r = 0.0, delta = 0.0, alpha = 0.0;
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    r = dot(cxy, cxy);
    delta = fwidth(r);
    alpha = 1.0 - smoothstep(1.0 - delta, 1.0 + delta, r);
    if (alpha < 0.5) // threshold
      discard;

    fragColor = vec4(co, (1-r)*.9   ); // apply alpha: (1-r) or r
  }
  """
    RNGBLRANG_FS = """
  out vec4 fragColor;

  float PI = 3.14159265359;

  uniform vec4 co;
  uniform float t;
  uniform float f;
  uniform float ang1;
  uniform float ang2;

  float roundedFrame (float d, float _thickness)
  {
    return smoothstep(0.55, 0.45, abs(d / _thickness) * 5.0);
  }

  void main()
  {
    float r = 0.0;
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    r = dot(cxy, cxy);

    float s = roundedFrame(r, 9.5);
    if (s < 0.05)
      discard; 

    // Use polar coordinates instead of cartesian
    vec2 toCenter = vec2(0.5)-gl_PointCoord.xy;
    float radius = length(toCenter)*2.0;
    float alpha = 1.0;

    float outter = 1.0;
    float rad = outter - t;
    float inner = rad - t;
    if (radius < inner)
      discard;

    float angle = atan(toCenter.y, -toCenter.x);
    angle = angle * 180 / PI;
    //if (angle < 0)
    //  angle = 360 - angle;

    if (angle > ang1 && angle < ang2)
      discard;

    if (radius > rad){
      alpha = smoothstep(outter, rad-f, radius);
    }
    else{
      alpha = smoothstep(inner, rad+f, radius);
    }

    fragColor = co;
    fragColor.a = alpha;
    fragColor.rgb = pow(fragColor.rgb, vec3(2.2));

    // fragColor.rgb = mix(co.rgb, vec3(0.0, 0.0, 1.0), angle/360.0);
  }
  """
    RNGBLR_FS = """
  out vec4 fragColor;

  uniform vec4 co;
  uniform float t;
  uniform float f;

  float roundedFrame (float d, float _thickness)
  {
    return smoothstep(0.55, 0.45, abs(d / _thickness) * 5.0);
  }

  void main()
  {
    float r = 0.0;
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    r = dot(cxy, cxy);

    float s = roundedFrame(r, 9.5);
    if (s < 0.05)
      discard; 

    // Use polar coordinates instead of cartesian
    vec2 toCenter = vec2(0.5)-gl_PointCoord.xy;
    // float angle = atan(toCenter.y,toCenter.x);
    float radius = length(toCenter)*2.0;
    float alpha = 1.0;

    float outter = 1.0;
    float rad = outter - t;
    float inner = rad - t;
    if (radius < inner)
      discard;


    if (radius > rad){
      alpha = smoothstep(outter, rad-f, radius);
    }
    else{
      alpha = smoothstep(inner, rad+f, radius);
    }

    fragColor = co;
    fragColor.a = alpha;
    fragColor.rgb = pow(fragColor.rgb, vec3(2.2));
  }
  """
    RNGBLRSLC_FS = """
  out vec4 fragColor;

  uniform vec4 co;
  uniform float t;
  uniform vec4 mask;

  void main()
  {
    if (gl_PointCoord.x < mask.x || gl_PointCoord.x > mask.y)
      discard;
    if (gl_PointCoord.y < mask.z || gl_PointCoord.y > mask.a)
      discard;
    
    // Use polar coordinates instead of cartesian
    vec2 toCenter = vec2(0.5)-gl_PointCoord.xy;
    float angle = atan(toCenter.y,toCenter.x);
    float radius = length(toCenter)*2.0;
    float alpha = 1.0;
    float mid = 1.0 - t;
    float inner = mid - t;

    if (radius < inner)
      discard;

    if (radius > mid)
      alpha = smoothstep(1.0, mid, radius);
    else
      alpha = smoothstep(inner, mid, radius);

    fragColor = co;
    fragColor.a *= alpha;
    fragColor.rgb = pow(fragColor.rgb, vec3(2.2));
  }
  """
    RTCROMASLLIN_FS = """
  float PI_4 = 0.785398;
  uniform float h;
  out vec4 fragColor;
  vec3 hsv2rgb(vec3 c)
  {
      vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
      vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
      return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
  }
  void main()
  {
    float S = mix(0, 1, gl_PointCoord.x);
    float V = mix(1, 0, gl_PointCoord.y);
    fragColor.rgb = pow(hsv2rgb(vec3(h, S, V)), vec3(2.2)); // hsv2rgb(vec3(h, S, V)); //
    fragColor.a = 1.0;
  }
  """
    CRNGCROMLINH_FS = """
  #define TWO_PI 6.28318530718

  uniform float s; // saturation
  uniform float v; // value (lum)
  out vec4 fragColor;
  vec3 hsb2rgb(in vec3 c){
    vec3 rgb = clamp(abs(mod(c.x*6.0+vec3(0.0,4.0,2.0),
                              6.0)-3.0)-1.0,
                      0.0,
                      1.0 );
    rgb = rgb*rgb*(3.0-2.0*rgb);
    return c.z * mix( vec3(1.0), rgb, c.y); // * value // OLD
  }

  void main()
  {
    float r1 = 1.0;
    float r2 = .5;

    float r = 0.0, delta = 0.0, alpha = 0.0;
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    r = dot(cxy, cxy);
    delta = fwidth(r);
    alpha = 1.0 - smoothstep(1.0 - delta, 1.0 + delta, r);
    if (alpha < 0.05) // threshold
      discard;

    // Use polar coordinates instead of cartesian
    vec2 toCenter = vec2(0.5)-gl_PointCoord.xy;
    float angle = atan(toCenter.y,toCenter.x);
    float radius = length(toCenter)*2.0;

    if (radius < .82)
      discard;

    if (radius >= .82 && radius < .85)
      alpha = smoothstep(.82, .85, radius);

    // Map the angle (-PI to PI) to the Hue (from 0 to 1)
    // and the Saturation to the radius
    vec3 co = hsb2rgb(vec3((angle/TWO_PI)+0.5, s, v));
    // fragColor.rgb = co;
    fragColor.rgb = pow(co, vec3(2.2)); // co
    fragColor.a = alpha;
  }
  """
    SHCx4343524F4D415F48 = (CF_VS, CRNGCROMLINH_FS)
    SHCx5243524f4d415f534c5f4c494e = (CF_VS, RTCROMASLLIN_FS)
    RNGS_SPLITANG_FS = """
  out vec4 fragColor;

  float PI_2 = 6.283185;
  float DEG_RAD = 0.0174;
  float PI_4 = 0.785398;
  float PI = 3.14159265359;

  uniform vec4 co;
  uniform float e1;
  uniform float e2;
  uniform float f;
  uniform float n;
  uniform int act;

  float roundedFrame (float d, float thickness)
  {
    return smoothstep(0.55, 0.45, abs(d / thickness) * 5.0);
  }

  void main()
  {
    float r = 0.0;
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    r = dot(cxy, cxy);

    float s = roundedFrame(r, 9.5);
    if (s < 0.05)
      discard;

    // Use polar coordinates instead of cartesian
    vec2 toCenter = vec2(0.5)-gl_PointCoord.xy;
    float radius = length(toCenter)*2.0;

    if (radius < e1)
      discard;

    vec4 color = co;
    bool ok = false;
    float angle = atan(toCenter.y, toCenter.x);
    if (gl_PointCoord.y > 0.5){
      angle *= -1;
      ok = act < 0; //act >= floor(n/2.);
    }
    else{
      ok = act >= 0; // act < floor(n/2.);
    }

    float mini_angle = PI_2 / n;
    float pos_angle = 0.0;
    vec2 act_range_angle = vec2(mini_angle * act, mini_angle * (act + 1));
    if (!ok)
      act_range_angle *= vec2(-1.);
    for(int i = 0; i < n; i++){
      if (angle + DEG_RAD > pos_angle && angle - DEG_RAD < pos_angle)
        color.rgb = color.rgb * .25f;
        //discard;
      if (ok && angle > act_range_angle.x && angle < act_range_angle.y)
        color.rgb = mix(color.rgb, color.rgb * 1.15f, radius*2);
      else if (ok && angle * -1 > act_range_angle.x && angle * -1 < act_range_angle.y)
        color.rgb = mix(color.rgb, color.rgb * 1.15f, radius*2);
      pos_angle = mini_angle * i;
    }

    float alpha = 1.0;
    if (radius >= e1 && radius < e2*f)
      alpha = smoothstep(e1, e2*f, radius);

    fragColor = color;
    fragColor.a *= alpha*s;
    fragColor.rgb = pow(fragColor.rgb, vec3(2.2));
  }
  """
    CRNGCROMLINW_FS = """
  #define RAD 1.5708
  #define RAD_2 RAD/2
  #define PI 3.14159265359
  #define PI_6 PI/3+RAD_2
  const vec3 red = vec3(1, 0, 0);
  const vec3 green = vec3(0, 1, 0);
  const vec3 blue = vec3(0, 0, 1);
  out vec4 fragColor;
  vec3 hsb2rgb(in vec3 c){
    vec3 rgb = clamp(abs(mod(c.x*6.0+vec3(0.0,4.0,2.0),
                              6.0)-3.0)-1.0,
                      0.0,
                      1.0 );
    rgb = rgb*rgb*(3.0-2.0*rgb);
    return c.z * mix( vec3(1.0), rgb, c.y); // * value // OLD
  }

  void main()
  {
    float r = 0.0, delta = 0.0, alpha = 0.0;
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    r = dot(cxy, cxy);
    delta = fwidth(r);
    alpha = 1.0 - smoothstep(1.0 - delta, 1.0 + delta, r);
    if (alpha < 0.05) // threshold
      discard;


    vec2 toCenter = vec2(0.5)-gl_PointCoord.xy;
    float angle = atan(toCenter.x,toCenter.y);
    float radius = length(toCenter)*2.0;
    
    if (abs(angle) > 3*PI/4)
      discard;

    angle *= 1.2;
    

    if (radius < .82)
      discard;

    if (radius >= .82 && radius < .85)
      alpha = smoothstep(.82, .85, radius);

    vec3 co = hsb2rgb(vec3((angle/PI_6)+0.55, 1.0, 1.0));
    
    //vec3 co = vec3(cxy.x, cxy.y, 1.0);
    
    fragColor.rgb = pow(co, vec3(2.2)); // co
    fragColor.a = alpha;
  }
  """

    ''' SHADER CODES '''  # TODO: Make it beautiful, PLEASE...
    # RINGS
    # SHCx524E4753 = (CF_VS, RNGS_FS)

    SHCx524E47424C521197 = (CF_VS, RNGBLRANG_FS)
    SHCx524E47424C52 = (CF_VS, RNGBLR_FS)
    SHCx524E47535F53504C4954414E47 = (CF_VS, RNGS_SPLITANG_FS)
    SHCx524E47424C5218103 = (CF_VS, RNGBLRSLC_FS)
    SHCx43524e4743524f4d4c494e57 = (CF_VS, CRNGCROMLINW_FS)

    # CIRCLES
    SHCx434653 = (CF_VS, CFS2_FS)
    SHCx434653_2 = (CF_VS, CFS2_GAMMA_FS)
    SHCx4346535F43524F50544F50 = (CF_VS, CFS_CROPTOP_FS)
    SHCx4346535F43524F50424F54 = (CF_VS, CFS_CROPBOT_FS)

    # SHCx4346535F41415F424C52 = (CF_VS, CFS_AA_BLR_FS)

    # CROMA
    # SHCx4343524F4D415F48 = (CF_VS, CRCROMA_H_FS)
    # SHCx4343524F4D415F4853 = (CF_VS, CCROMA_HS_FS)
    # SHCx4343524F4D415F534C = (CF_VS, RCROMA_SL_FS)

    # IMAGES
    SHCx494D4741 = (IMG_VS, IMGA_FS)
    SHCx494D47415F47414D434F = (IMG_VS, IMGA_GAMMCORR_FS)
    SHCx494D47415F47414D434F5F424F4F5354 = (IMG_VS, IMGA_GAMMCORR_BOOST_FS)
    SHCx494D47415F47414D4D415F4F50 = (IMG_VS, IMGA_GAMMA_OP)

    # OTHERS
    SHCx504C49474854 = (CF_VS, PLIGHT_FS)

    # RECT
    # SHCx525F4141 = (CF_VS, R_AA_FS)

    ''' SHADER GEOMETRY '''
    def get_img_geom(*args):
        return {"p": get_img_verts(*args), "texco": get_tex_coord()}

    def get_tex_coord():
        return ((0, 1), (0, 0), (1, 0), (1, 1))

    def get_img_verts(*args):
        x, y = args[0]
        w, h = args[1]
        return [
            [x,     y + h],
            [x,     y],
            [x + w, y],
            [x + w, y + h]
        ]

    def get_cir_geom(p):
      return {"p": [p]}

    class ShaderGeom(Enum):
        IMG = get_img_geom
        IMG_V = get_img_verts
        IMG_TC = get_tex_coord  # Ref: https://docs.blender.org/api/blender2.8/gpu.html#d-image
        CIR = get_cir_geom     # https://docs.blender.org/api/blender2.8/gpu.html#d-rectangle

        def __call__(self, *args):
            return self.value(*args[0])
