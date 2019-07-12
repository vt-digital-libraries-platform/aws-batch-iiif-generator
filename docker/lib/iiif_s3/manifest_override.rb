module IiifS3

  module ManifestOverride

    # @return [String] The IIIF default type for a manifest.
    TYPE = "sc:Manifest"

    include BaseProperties

    #
    # @return [String]  the JSON-LD representation of the manifest as a string.
    # 
    def to_json
      obj = base_properties

     obj["thumbnail"] =
      {
        "@id"   => @primary.variants["thumbnail"].uri,
        "@type": "dctypes:Image",
        "width" => @primary.variants["thumbnail"].width,
        "height" => @primary.variants["thumbnail"].height,
        "service" => {
          "@context" => IiifS3::IMAGE_CONTEXT,
          "@id" => @primary.variants["thumbnail"].id,
          "profile" => IiifS3::LEVEL_0,
        },
      }
      obj["viewingDirection"] = @primary.viewing_direction 
      obj["viewingHint"] = @primary.is_document ? "paged" : "individuals"
      obj["sequences"] = [@sequences]

      return JSON.pretty_generate obj
    end

    #--------------------------------------------------------------------------
    def build_canvas(data)

      canvas_id = generate_id "#{data.id}/canvas/#{data.section}"

      obj = {
        "@type" => CANVAS_TYPE,
        "@id"   => canvas_id,
        "label" => data.section_label,
        "width" => data.variants["full"].width.floor,
        "height" => data.variants["full"].height.floor,
        "thumbnail" =>
        {
         "@id"   => data.variants["thumbnail"].uri,
         "@type": "dctypes:Image",
         "width" => data.variants["thumbnail"].width,
         "height" => @primary.variants["thumbnail"].height,
         "service" => {
           "@context" => IiifS3::IMAGE_CONTEXT,
           "@id" => data.variants["thumbnail"].id,
           "profile" => IiifS3::LEVEL_0
          }
        }
      }
      obj["images"] = [build_image(data, obj)]

      # handle objects that are less than 1200px on a side by doubling canvas size
      if obj["width"] < MIN_CANVAS_SIZE || obj["height"] < MIN_CANVAS_SIZE
        obj["width"]  *= 2
        obj["height"] *= 2
      end
      return obj
    end
  end
end
